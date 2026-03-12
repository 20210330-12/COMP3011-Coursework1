from django.shortcuts import render
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError


@extend_schema(tags=["Posts"])
@extend_schema_view(
    get=extend_schema(summary="List all community posts"),
    post=extend_schema(summary="Create a new community post"),
)
class PostListCreateView(generics.ListCreateAPIView):
    # queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Post.objects
            .select_related("author", "related_team", "related_player")
            .annotate(
                comment_count=Count("comments", distinct=True),
                like_count=Count("liked_by", distinct=True),
            )
        )

        related_team = self.request.query_params.get("related_team")
        related_player = self.request.query_params.get("related_player")
        author = self.request.query_params.get("author")

        if related_team:
            queryset = queryset.filter(related_team_id=related_team)
        if related_player:
            queryset = queryset.filter(related_player_id=related_player)
        if author:
            queryset = queryset.filter(author_id=author)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema(tags=["Posts"])
@extend_schema_view(
    get=extend_schema(summary="Retrieve post details"),
    put=extend_schema(summary="Update a post"),
    patch=extend_schema(summary="Partially update a post"),
    delete=extend_schema(summary="Delete a post"),
)
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return (
            Post.objects
            .select_related("author", "related_team", "related_player")
            .annotate(
                comment_count=Count("comments", distinct=True),
                like_count=Count("liked_by", distinct=True),
            )
        )


@extend_schema(tags=["Comments"])
@extend_schema_view(
    get=extend_schema(
        summary="List comments for a post",
        parameters=[
            OpenApiParameter(
                name="post_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID of the post whose comments should be returned",
            ),
        ],
    ),
    post=extend_schema(summary="Create a new comment"),
)
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = (
            Comment.objects
            .select_related("author", "post")
            .annotate(like_count=Count("liked_by", distinct=True))
            .order_by("created_at", "id")
        )

        post_id = self.request.query_params.get("post_id")

        if self.request.method == "GET" and not post_id:
            raise ValidationError({"post_id": "This query parameter is required."})

        return queryset.filter(post_id=post_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema(tags=["Comments"])
@extend_schema_view(
    get=extend_schema(summary="Retrieve comment details"),
    put=extend_schema(summary="Update a comment"),
    patch=extend_schema(summary="Partially update a comment"),
    delete=extend_schema(summary="Delete a comment"),
)
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return (
            Comment.objects
            .select_related("author", "post")
            .annotate(like_count=Count("liked_by", distinct=True))
        )


@extend_schema(tags=["Posts"])
class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Like a post",
        description="Adds the authenticated user's like to the specified post."
    )
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.liked_by.add(request.user)
        return Response(
            {"detail": "Post liked successfully.", "like_count": post.liked_by.count()},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Remove like from a post",
        description="Removes the authenticated user's like from the specified post."
    )
    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.liked_by.remove(request.user)
        return Response(
            {"detail": "Post like removed successfully.", "like_count": post.liked_by.count()},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Comments"])
class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Like a comment",
        description="Adds the authenticated user's like to the specified comment."
    )
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.liked_by.add(request.user)
        return Response(
            {"detail": "Comment liked successfully.", "like_count": comment.liked_by.count()},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Remove like from a comment",
        description="Removes the authenticated user's like from the specified comment."
    )
    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.liked_by.remove(request.user)
        return Response(
            {"detail": "Comment like removed successfully.", "like_count": comment.liked_by.count()},
            status=status.HTTP_200_OK,
        )