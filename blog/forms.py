from django import forms

from . import models


class TagForm(forms.ModelForm):
    """
    Form for tag model.
    """

    class Meta:
        """
        Link to tag model and form basic setup.
        """
        model = models.Tag
        fields = ('name', 'subheading', 'image', 'overview')

        # Modify image label from model default.
        labels = {
            'image': 'Main image',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify form HTML (classes set for bootstrap).
        self.fields['name'].widget.attrs.update({'class': 'rounded-0'})
        self.fields['subheading'].widget.attrs.update({'class': 'rounded-0',
                                                       'rows': '2'})
        self.fields['overview'].widget.attrs.update({'class': 'rounded-0'})
        self.fields['image'].widget.attrs.update({'class': 'rounded-0'})


class PostForm(forms.ModelForm):
    """
    Form for post model.
    """

    class Meta:
        """
        Link to post model and basic form setup.
        """
        model = models.Post
        fields = ('title', 'subheading', 'tags', 'image', 'text')

        # Modify image label from model default.
        labels = {
            'image': 'Main image',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify form HTML (classes set for bootstrap).
        self.fields['title'].widget.attrs.update({'class': 'rounded-0'})
        self.fields['subheading'].widget.attrs.update({'class': 'rounded-0',
                                                       'rows': '2'})
        self.fields['tags'].widget.attrs.update({'class': 'rounded-0'})
        self.fields['image'].widget.attrs.update({'class': 'rounded-0'})


class CommentForm(forms.ModelForm):
    """
    Form for comment model.
    """

    class Meta:
        """
        Link to comment model and basic form setup.
        """
        model = models.Comment
        fields = ('text',)

        # Remove text label.
        labels = {
            'text': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify form HTML (classes set for bootstrap).
        self.fields['text'].widget.attrs.update({'class': 'rounded-0',
                                                 'rows': '2',
                                                 'placeholder': 'Write a comment...'})


class SearchPostForm(forms.Form):
    """
    Form used to obtain user inputs for searching all posts.
    """
    post_input = forms.CharField(max_length=100, required=False)

    # Set tag choices from database.
    tag_input = forms.ModelChoiceField(label='Topic',
                                       queryset=models.Tag.objects.all(),
                                       empty_label="All",
                                       to_field_name="name",
                                       required=False)

    order_input = forms.ChoiceField(
        label='Sort', choices=((0, 'New'), (1, 'Old')))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify form HTML (classes set for bootstrap).
        self.fields['post_input'].widget.attrs.update({
            'class': 'rounded-0 form-control form-control-md',
            'placeholder': "Search posts"
        })
        self.fields['tag_input'].widget.attrs.update(
            {'class': 'rounded-0 custom-select'})
        self.fields['order_input'].widget.attrs.update(
            {'class': 'rounded-0 custom-select'})


class SearchDraftForm(forms.Form):
    """
    Form used to obtain staff user inputs for searching user drafts.
    """
    post_input = forms.CharField(
        label='Search', max_length=100, required=False)

    # Set tag choices from database.
    tag_input = forms.ModelChoiceField(label='Topic',
                                       queryset=models.Tag.objects.all(),
                                       empty_label="All",
                                       to_field_name="name",
                                       required=False)

    order_input = forms.ChoiceField(
        label='Sort', choices=((0, 'New'), (1, 'Old')))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify form HTML (classes set for bootstrap).
        self.fields['post_input'].widget.attrs.update({
            'class': 'rounded-0 form-control form-control-md',
            'placeholder': "Search drafts"
        })
        self.fields['tag_input'].widget.attrs.update(
            {'class': 'rounded-0 custom-select'})
        self.fields['order_input'].widget.attrs.update(
            {'class': 'rounded-0 custom-select'})


class SearchTagForm(forms.Form):
    """
    Form used to obtain user inputs for searching all tags.
    """
    name_input = forms.CharField(label='Search',
                                 max_length=100,
                                 required=False,
                                 widget=forms.TextInput(attrs={'placeholder': "Search topics"}))
    order_input = forms.ChoiceField(label='Sort by', choices=(
        (0, 'Most posts'), (1, 'Least posts'), (2, 'A-Z'), (3, 'Z-A')))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify form HTML (classes set for bootstrap)
        self.fields['name_input'].widget.attrs.update({
            'class': 'rounded-0 form-control form-control-md',
            'placeholder': "Search topics"
        })
        self.fields['order_input'].widget.attrs.update(
            {'class': 'rounded-0 custom-select'})
