from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.LandingPage.as_view(), name='landing'),
    path('post/create/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/update/<int:pk>/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/delete/<int:pk>/',views.PostDeleteView.as_view(), name='post-delete'),
    path('search/', views.SearchView.as_view(), name='post-search'),
    # The returns a list of posts filtered by tag slugs that meet the url slug.
    path('search/pre_search/<slug>/', views.SearchView.as_view(), name='post-pre-search'),
    path('<username>/drafts/', views.UserDraftListView.as_view(), name='user-post-list'),
    path('post/<int:pk>/comments/', views.CommentListView.as_view(), name='post-comments'),
    path('comment/delete/<int:pk>/', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('comment/update/<int:pk>/', views.CommentUpdateView.as_view(), name='comment-update'),
    path('post/publish/<int:pk>/', views.post_publish, name='post_publish'),
    path('tag/create/', views.TagCreateView.as_view(), name='tag-create'),
    path('tag/list/', views.TagListView.as_view(), name='tag-list'),
    path('tag/overview/<slug>/', views.TagOverviewView.as_view(), name='tag-overview'),
    path('tag/update/<slug>/', views.TagUpdateView.as_view(), name='tag-update'),
    path('tag/delete/<slug>/',views.TagDeleteView.as_view(), name='tag-delete'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
