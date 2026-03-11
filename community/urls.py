from django.urls import path
from .views import PostListCreateView, PostDetailView, CommentListCreateView

urlpatterns = [
    path("posts/", PostListCreateView.as_view()),
    path("posts/<int:pk>/", PostDetailView.as_view()),
    path("comments/", CommentListCreateView.as_view()),
]