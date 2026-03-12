from django.urls import path
from .views import PostListCreateView, PostDetailView, CommentListCreateView, CommentDetailView, PostLikeView, CommentLikeView

urlpatterns = [
    path("posts/", PostListCreateView.as_view(), name="post-list-create"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("posts/<int:pk>/like/", PostLikeView.as_view(), name="post-like"),
    path("comments/<int:pk>/like/", CommentLikeView.as_view(), name="comment-like"),
]