from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from football.models import Team
from .models import UserProfile


class AccountsAPITestCase(APITestCase):
    def setUp(self):
        self.team = Team.objects.create(
            external_id="team-1",
            name="Arsenal",
            short_name="ARS",
            country="England",
            competition="Premier League",
            season=2023,
            stadium="Emirates Stadium",
            founded=1886,
        )

        self.password = "strongpassword123"
        self.user = User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password=self.password,
        )

        UserProfile.objects.create(
            user=self.user,
            display_name="Existing User",
            bio="Existing bio",
            favourite_team=self.team,
        )

    def test_register_user_successfully(self):
        url = reverse("register")
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "verystrongpassword123",
            "display_name": "New User",
            "bio": "Hello there",
            "favourite_team": self.team.id,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")
        self.assertEqual(response.data["user"]["profile"]["display_name"], "New User")
        self.assertEqual(response.data["user"]["profile"]["bio"], "Hello there")
        self.assertEqual(response.data["user"]["profile"]["favourite_team"], self.team.id)
        self.assertEqual(
            response.data["user"]["profile"]["favourite_team_name"],
            self.team.name,
        )

        created_user = User.objects.get(username="newuser")
        self.assertTrue(created_user.check_password("verystrongpassword123"))
        self.assertEqual(created_user.profile.display_name, "New User")

    def test_login_returns_token_and_profile(self):
        url = reverse("login")
        payload = {
            "username": self.user.username,
            "password": self.password,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], self.user.username)
        self.assertEqual(
            response.data["user"]["profile"]["display_name"],
            "Existing User",
        )

    def test_login_fails_with_invalid_credentials(self):
        url = reverse("login")
        payload = {
            "username": self.user.username,
            "password": "wrongpassword",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"], "Invalid credentials")

    def test_me_requires_authentication(self):
        url = reverse("me")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_authenticated_user(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        url = reverse("me")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["profile"]["display_name"], "Existing User")
        self.assertEqual(response.data["profile"]["favourite_team"], self.team.id)

    def test_logout_deletes_auth_token(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        url = reverse("logout")
        response = self.client.post(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful")
        self.assertFalse(Token.objects.filter(key=token.key).exists())

    def test_delete_account_removes_user(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        url = reverse("delete-account")
        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Account deleted successfully")
        self.assertFalse(User.objects.filter(username="existinguser").exists())