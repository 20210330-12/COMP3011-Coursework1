from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from community.models import Post, Comment
from football.models import Team, Player
from accounts.models import UserProfile


class CommunityAPITestCase(APITestCase):
    def setUp(self):
        self.team = Team.objects.create(
            external_id="team-10",
            name="Liverpool",
            short_name="LIV",
            country="England",
            competition="Premier League",
            season=2023,
            stadium="Anfield",
            founded=1892,
        )

        self.player = Player.objects.create(
            external_id="player-10",
            name="Mohamed Salah",
            full_name="Mohamed Salah",
            nationality="Egypt",
            position="Forward",
            current_team=self.team,
            preferred_foot="Left",
        )

        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="authorpass123",
        )
        UserProfile.objects.create(
            user=self.author,
            display_name="Author User",
            bio="",
            favourite_team=self.team,
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
        )
        UserProfile.objects.create(
            user=self.other_user,
            display_name="Other User",
            bio="",
            favourite_team=self.team,
        )

        self.author_token = Token.objects.create(user=self.author)
        self.other_token = Token.objects.create(user=self.other_user)

        self.post = Post.objects.create(
            author=self.author,
            title="Liverpool discussion",
            content="Great performance this week.",
            related_team=self.team,
            related_player=self.player,
        )

        self.comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content="First comment",
        )

    def authenticate_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token.key}")

    def authenticate_other_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.other_token.key}")

    def test_anonymous_user_can_list_posts(self):
        url = reverse("post-list-create")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Liverpool discussion")
        self.assertEqual(response.data["results"][0]["comment_count"], 1)
        self.assertEqual(response.data["results"][0]["like_count"], 0)
        self.assertFalse(response.data["results"][0]["is_liked_by_me"])

    def test_authenticated_user_can_create_post(self):
        self.authenticate_author()
        url = reverse("post-list-create")

        payload = {
            "title": "New post title",
            "content": "New post content",
            "related_team": self.team.id,
            "related_player": self.player.id,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

        created_post = Post.objects.latest("id")
        self.assertEqual(created_post.author, self.author)
        self.assertEqual(created_post.related_team, self.team)
        self.assertEqual(created_post.related_player, self.player)

    def test_anonymous_user_cannot_create_post(self):
        url = reverse("post-list-create")
        payload = {
            "title": "Unauthenticated post",
            "content": "Should fail",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_author_can_update_post(self):
        self.authenticate_other_user()
        url = reverse("post-detail", kwargs={"pk": self.post.id})

        response = self.client.patch(
            url,
            {"title": "Hacked title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Liverpool discussion")

    def test_author_can_update_own_post(self):
        self.authenticate_author()
        url = reverse("post-detail", kwargs={"pk": self.post.id})

        response = self.client.patch(
            url,
            {"title": "Updated by author"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated by author")

    def test_post_list_can_filter_by_related_team(self):
        other_team = Team.objects.create(
            external_id="team-20",
            name="Arsenal",
            short_name="ARS",
            country="England",
            competition="Premier League",
            season=2023,
            stadium="Emirates Stadium",
            founded=1886,
        )

        Post.objects.create(
            author=self.author,
            title="Arsenal post",
            content="Another discussion",
            related_team=other_team,
        )

        url = reverse("post-list-create")
        response = self.client.get(url, {"related_team": self.team.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Liverpool discussion")

    def test_comment_list_can_be_filtered_by_post_id(self):
        other_post = Post.objects.create(
            author=self.author,
            title="Another post",
            content="Another content",
        )
        Comment.objects.create(
            post=other_post,
            author=self.author,
            content="Comment for another post",
        )

        url = reverse("comment-list-create")
        response = self.client.get(url, {"post_id": self.post.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["content"], "First comment")

    def test_authenticated_user_can_create_comment(self):
        self.authenticate_author()
        url = reverse("comment-list-create")

        payload = {
            "post": self.post.id,
            "content": "A new comment from the author",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

        created_comment = Comment.objects.latest("id")
        self.assertEqual(created_comment.author, self.author)
        self.assertEqual(created_comment.post, self.post)

    def test_only_author_can_update_comment(self):
        self.authenticate_other_user()
        url = reverse("comment-detail", kwargs={"pk": self.comment.id})

        response = self.client.patch(
            url,
            {"content": "Edited by other user"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "First comment")

    def test_author_can_update_own_comment(self):
        self.authenticate_author()
        url = reverse("comment-detail", kwargs={"pk": self.comment.id})

        response = self.client.patch(
            url,
            {"content": "Edited by author"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Edited by author")

    def test_like_and_unlike_post(self):
        self.authenticate_author()
        like_url = reverse("post-like", kwargs={"pk": self.post.id})

        like_response = self.client.post(like_url, format="json")
        self.assertEqual(like_response.status_code, status.HTTP_200_OK)
        self.assertEqual(like_response.data["detail"], "Post liked successfully.")
        self.assertEqual(like_response.data["like_count"], 1)
        self.assertTrue(self.post.liked_by.filter(id=self.author.id).exists())

        unlike_response = self.client.delete(like_url, format="json")
        self.assertEqual(unlike_response.status_code, status.HTTP_200_OK)
        self.assertEqual(unlike_response.data["detail"], "Post like removed successfully.")
        self.assertEqual(unlike_response.data["like_count"], 0)
        self.assertFalse(self.post.liked_by.filter(id=self.author.id).exists())

    def test_like_and_unlike_comment(self):
        self.authenticate_author()
        like_url = reverse("comment-like", kwargs={"pk": self.comment.id})

        like_response = self.client.post(like_url, format="json")
        self.assertEqual(like_response.status_code, status.HTTP_200_OK)
        self.assertEqual(like_response.data["detail"], "Comment liked successfully.")
        self.assertEqual(like_response.data["like_count"], 1)
        self.assertTrue(self.comment.liked_by.filter(id=self.author.id).exists())

        unlike_response = self.client.delete(like_url, format="json")
        self.assertEqual(unlike_response.status_code, status.HTTP_200_OK)
        self.assertEqual(unlike_response.data["detail"], "Comment like removed successfully.")
        self.assertEqual(unlike_response.data["like_count"], 0)
        self.assertFalse(self.comment.liked_by.filter(id=self.author.id).exists())
    
    def test_comment_list_requires_post_id_query_parameter(self):
        url = reverse("comment-list-create")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("post_id", response.data)