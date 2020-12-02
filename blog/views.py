from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models.functions import Lower
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View, generic
from django.views.generic.detail import SingleObjectMixin

from . import forms, models


### Authentication checkers ###
class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin to check if user is staff.
    """

    def test_func(self):
        return self.request.user.is_staff


### LANDING VIEWS ###
class LandingPage(generic.TemplateView):
    """
    Landing page displaying 4 most recent posts and 4 most posted topics.
    """
    template_name = 'blog/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add tags context with 4 most posted topics
        context['tags'] = models.Tag.objects.annotate(
            num_posts=Count('posts')).order_by('-num_posts')[:4]

        # Add posts context with 4 most recent posts
        context['posts'] = models.Post.objects.filter(
            publish_date__isnull=False).order_by('-publish_date')[:4]

        return context


### POST VIEWS ###
class PostCreateView(StaffRequiredMixin, SuccessMessageMixin,
                     generic.CreateView):
    """
    Post create view accessible by any user with staff privileges.
    """
    form_class = forms.PostForm
    model = models.Post

    # On success, display message on base template.
    success_message = "%(title)s was created successfully"

    def form_valid(self, form_class):
        """
        Additional to base, sets user as post author.
        """
        form_class.instance.author = self.request.user
        return super().form_valid(form_class)


class PostDetailView(View):
    """
    Post detail selects CBV depending on the request HTTP method (POST/GET).
    """

    def get(self, *args, **kwargs):
        """
        For GET method select PostDisplay as view.
        """
        view = PostDisplay.as_view()
        return view(self.request, *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        For POST method select Comment as view.
        """
        view = Comment.as_view()
        return view(self.request, *args, **kwargs)


class PostDisplay(generic.DetailView):
    """
    GET method for PostDetailView. Displays post, comments and comment form.
    """
    model = models.Post

    def get_object(self):
        """
        Checks if post not published and user not author. Returns post object.
        """
        obj = super().get_object()
        if obj.publish_date is None and self.request.user != obj.author:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add comments and comment form as additional context.
        context['form'] = forms.CommentForm
        context['comments'] = self.object.comments.order_by('-created_date')

        return context


class SearchView(generic.ListView):
    """
    List view of all posts with search, filter and sort functionality.
    """
    template_name = 'blog/search.html'
    context_object_name = "posts"
    paginate_by = 12
    search_form = forms.SearchPostForm

    def get_queryset(self):
        """
        Modifies queryset based on user input to form and returns.
        """
        form = self.search_form(self.request.GET)

        # If valid form data submitted (HTTP GET).
        if form.is_valid():

            # Obtain form data.
            tag_filter = form.cleaned_data['tag_input']
            post_filter = form.cleaned_data['post_input']
            order_by = form.cleaned_data['order_input']

            # Base queryset, filtered to show posts that have been published.
            queryset = models.Post.objects.filter(publish_date__isnull=False)

            # Chain queryset dependent on user search form input.
            if tag_filter is not None:
                queryset = queryset.filter(tags__name__iexact=str(tag_filter))
            if post_filter is not None:
                queryset = queryset.filter(title__icontains=post_filter)
            if order_by == '0':
                queryset = queryset.order_by('-publish_date')
            elif order_by == '1':
                queryset = queryset.order_by('publish_date')

            # Set search_form values so they are displayed on post-search render.
            self.search_form = form

        # If form data not submitted.
        else:
            # If URL contains a tag slug, filter queryset by the slug. This is
            # done if  the pre-search URL is used to access this view. This is
            # used if the user selects all posts from a tag detail page.
            # Set the search form tag value to show the tag on the page render.
            try:
                queryset = models.Post.objects.filter(publish_date__isnull=False).filter(
                    tags__slug__iexact=self.kwargs['slug']).order_by('-publish_date')

                self.search_form = self.search_form({
                    'tag_input': models.Tag.objects.get(slug=self.kwargs['slug']),
                    'order_input': 0
                })

            # If accessing the URL slug kwarg throws an exception (i.e. the
            # pre-search URL has not been used to access the view) set queryset
            # to return all publish posts with newest first.
            except:
                queryset = models.Post.objects.filter(
                    publish_date__isnull=False).order_by('-publish_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add search form to context.
        context['search_form'] = self.search_form

        return context


class UserDraftListView(StaffRequiredMixin, generic.ListView):
    """
    List view of user's drafts with search, filter and sort functionality.
    """
    template_name = 'blog/user_draft_list.html'
    context_object_name = "posts"
    search_form = forms.SearchDraftForm
    paginate_by = 12

    def get_queryset(self):
        """
        Modifies queryset based on user input to form and returns.
        """
        username = self.kwargs['username']
        if not User.objects.filter(username=username).exists():
            raise Http404("User does not exist")
        else:
            if username != self.request.user.username:
                raise PermissionDenied()
            else:
                form = self.search_form(self.request.GET)

                # If valid form data submitted (GET).
                if form.is_valid():
                    # Obtain form data.
                    tag_filter = form.cleaned_data['tag_input']
                    post_filter = form.cleaned_data['post_input']
                    order_by = form.cleaned_data['order_input']

                    # Base queryset, filtered to show user posts that are not published.
                    queryset = models.Post.objects.filter(
                        publish_date__isnull=True).filter(author=self.request.user)

                    # Chain queryset dependent on user search form input.
                    if tag_filter is not None:
                        queryset = queryset.filter(tags__name__iexact=str(tag_filter))
                    if post_filter is not None:
                        queryset = queryset.filter(title__icontains=post_filter)
                    if order_by == '0':
                        queryset = queryset.order_by('-created_date')
                    elif order_by == '1':
                        queryset = queryset.order_by('created_date')

                    # Set search_form values so they are displayed on post-search render.
                    self.search_form = form

                # If form data not submitted, set queryset to return all user posts
                # that are not published with newest first.
                else:
                    queryset = models.Post.objects.filter(publish_date__isnull=True).filter(
                        author=self.request.user).order_by('-created_date')

                return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add search form to context data.
        context['search_form'] = self.search_form

        return context


class PostUpdateView(StaffRequiredMixin, SuccessMessageMixin,
                     generic.UpdateView):
    """
    Post update accessible by user with staff privileges and is post author.
    """
    form_class = forms.PostForm
    model = models.Post

    # On success, display message on base template.
    success_message = "%(title)s was edited successfully"

    def get_object(self):
        """
        Returns post object if post exists and user is post author.
        """
        obj = get_object_or_404(self.model, pk=self.kwargs.get('pk'))
        if obj.author == self.request.user:
            return obj
        else:
            raise PermissionDenied()

    def form_valid(self, form_class):
        """
        Additional to base, sets post edited date to current date.
        """
        self.object.edited_date = timezone.now()
        return super().form_valid(form_class)


class PostDeleteView(StaffRequiredMixin, generic.DeleteView):
    """
    Post delete accessible by any user with staff privileges.
    """
    model = models.Post
    context_object_name = "post"
    success_url = reverse_lazy('blog:landing')

    def delete(self, *args, **kwargs):
        """
        Additional to base, on success, displays message on base template.
        """
        messages.success(self.request, "Post deleted")
        return super().delete(*args, **kwargs)


### TAG VIEWS ###
class TagCreateView(StaffRequiredMixin, SuccessMessageMixin,
                    generic.CreateView):
    """
    Tag create view accessible by any user with staff privileges.
    """
    form_class = forms.TagForm
    model = models.Tag

    # On success, display message on base template.
    success_message = "%(name)s tag was created successfully"


class TagOverviewView(generic.DetailView):
    """
    Displays tag detail and 4 most recent published posts under that topic.
    """
    model = models.Tag

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adds post_list context with the 4 most recent posts under the topic.
        context['post_list'] = self.object.posts.filter(
            publish_date__isnull=False)[:4]

        return context


class TagListView(generic.ListView):
    """
    List view of all tags with search and sort functionality.
    """
    template_name = 'blog/tag_list.html'
    context_object_name = "tags"
    paginate_by = 12
    search_form = forms.SearchTagForm

    def get_queryset(self):
        """
        Modifies queryset based on user input to form and returns.
        """
        form = self.search_form(self.request.GET)

        # If valid form data submitted (GET).
        if form.is_valid():

            # Obtain form data.
            name_filter = form.cleaned_data['name_input']
            order_by = form.cleaned_data['order_input']

            # Base queryset, annotated with number of related posts.
            queryset = models.Tag.objects.all().annotate(num_posts=Count('posts'))

            # Chain queryset dependent on user search form input.
            if name_filter is not None:
                queryset = queryset.filter(name__icontains=name_filter)
            if order_by == '0':
                queryset = queryset.annotate(
                    num_posts=Count('posts')).order_by('-num_posts')
            if order_by == '1':
                queryset = queryset.annotate(
                    num_posts=Count('posts')).order_by('num_posts')
            if order_by == '2':
                queryset = queryset.annotate(
                    num_posts=Count('posts')).order_by(Lower('name'))
            if order_by == '3':
                queryset = queryset.annotate(num_posts=Count(
                    'posts')).order_by(Lower('name').desc())

            # Set search_form values so they are displayed on post-search render.
            self.search_form = form

        # If data not submitted, set queryset to return all tags annoted with
        # number of related posts and sorted by highest number of related posts.
        else:
            queryset = models.Tag.objects.annotate(
                num_posts=Count('posts')).order_by('-num_posts')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add search form to context data.
        context['search_form'] = self.search_form

        return context


class TagUpdateView(StaffRequiredMixin, SuccessMessageMixin,
                    generic.UpdateView):
    """
    Tag update view accessible by any user with staff privileges.
    """
    form_class = forms.TagForm
    model = models.Tag

    # On success, display message on base template.
    success_message = "%(name)s tag was edited successfully"


class TagDeleteView(StaffRequiredMixin, generic.DeleteView):
    """
    Tag delete view accessible by any user with staff privileges.
    """
    model = models.Tag
    context_object_name = "tag"
    success_url = reverse_lazy('blog:tag-list')

    def delete(self, *args, **kwargs):
        """
        Additional to base, on success, displays message on base template.
        """
        messages.success(self.request, "Topic deleted")
        return super().delete(*args, **kwargs)


### COMMENT VIEWS ###
class Comment(LoginRequiredMixin, SingleObjectMixin, generic.FormView):
    """
    POST method CBV for PostDetailView. Requires user to be logged in.
    """
    template_name = 'blog/post_detail.html'
    form_class = forms.CommentForm
    model = models.Post

    def form_valid(self, form_class):
        """
        Additional to base, sets author to user and saves post to comment.
        """
        form_class.instance.author = self.request.user
        form_class.instance.post = self.object
        form_class.instance.save()

        # On success, display message on base template.
        messages.success(self.request, "Comment posted successfully!")

        return super().form_valid(self.form_class)

    def post(self, *args, **kwargs):
        """
        Additional to base, sets post object to comment class object attribute.
        """
        self.object = self.get_object()

        # Raises HTTP 403 if post not published.
        if self.object.publish_date is None:
            raise PermissionDenied()

        return super().post(self.request, *args, **kwargs)

    def get_success_url(self):
        """
        Sets success URL as the current post detail page.
        """
        return reverse('blog:post-detail', kwargs={'pk': self.object.pk})


class CommentListView(generic.ListView):
    """
    Additonal comment list view if >10 comments under post.
    """
    template_name = 'blog/comment_list.html'
    context_object_name = "comments"
    paginate_by = 10

    def get_queryset(self):
        """
        Returns queryset with post comments and order with newest first.
        """
        return (models.Comment.objects
                .filter(post=self.kwargs.get('pk'))
                .order_by("-created_date"))


class CommentUpdateView(LoginRequiredMixin, generic.UpdateView):
    """
    Comment update accessible user who is logged in and is comment author.
    """
    form_class = forms.CommentForm
    model = models.Comment

    def get_object(self):
        """
        Returns object if exists and user has permission.
        """
        obj = get_object_or_404(self.model, pk=self.kwargs.get('pk'))
        if obj.author == self.request.user:
            return obj
        else:
            raise PermissionDenied()

    def form_valid(self, form_class):
        """
        Additional to base, sets edited date to current and displays message.
        """
        self.object.edited_date = timezone.now()
        messages.success(self.request, "Comment was edited successfully!")
        return super().form_valid(form_class)


class CommentDeleteView(LoginRequiredMixin, generic.DeleteView):
    """
    Comment delete accessible by user who is comment author or staff.
    """
    model = models.Comment

    def get_object(self):
        """
        Get comment object if user is comment author.
        """
        obj = get_object_or_404(self.model, pk=self.kwargs.get('pk'))
        if obj.author == self.request.user or self.request.user.is_staff:
            return obj
        else:
            raise PermissionDenied()

    def get_success_url(self):
        """
        Sets success URL as the current post detail page.
        """
        return reverse('blog:post-detail', kwargs={'pk': self.object.post.pk})

    def delete(self, *args, **kwargs):
        """
        Additional to base, on success, displays message on base template.
        """
        messages.success(self.request, "Comment deleted")
        return super().delete(*args, **kwargs)


### More funtionality ###
def is_staff(user):
    """
    Callable returning if user is staff for user_passes_test decorator.
    """
    return user.is_staff


@user_passes_test(is_staff, login_url='/', redirect_field_name=None)
def post_publish(request, pk):
    """
    Sets publish date to current date.
    """
    post = get_object_or_404(models.Post, pk=pk)
    post.publish()
    messages.success(request, "Published!")
    return redirect('blog:post-detail', pk=post.pk)
