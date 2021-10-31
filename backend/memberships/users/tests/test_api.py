import pytest

from memberships.users.api.serializers import UserSerializer
from memberships.users.models import User


pytestmark = pytest.mark.django_db


class TestAuthenticationFlow:
    def test_register(self, api_client):
        response = api_client.post(
            "/api/auth/register/",
            {
                "username": "ashok",
                "email": "ashok@gmail.com",
                "password1": "s3cr3tP@55w0rd",
                "password2": "s3cr3tP@55w0rd",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json() == {
            "username": "ashok",
            "name": "",
            "about": "",
            "avatar": {},
            "cover": {},
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "user_preferences": {
                "is_accepting_payments": True,
                "minimum_amount": "10.00",
            },
            "follower_count": 0,
            "subscriber_count": 0,
        }
        assert User.objects.get(username="ashok").email == "ashok@gmail.com"

    def test_me(self, user, api_client):
        api_client.force_authenticate(user)
        response = api_client.get("/api/me/")
        assert response.status_code == 200
        assert response.json() == {
            "username": user.username,
            "name": user.name,
            "about": "",
            "avatar": {},
            "cover": {},
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "user_preferences": {
                "is_accepting_payments": True,
                "minimum_amount": "10.00",
            },
            "follower_count": 0,
            "subscriber_count": 0,
        }

    def test_update(self, user, api_client):
        api_client.force_authenticate(user)
        response = api_client.patch(
            "/api/me/",
            {
                "about": "Hello world! this is me!",
                "social_links": {
                    "website_url": "https://google.com",
                    "youtube_url": "https://youtube.com",
                    "facebook_url": "https://fb.com",
                    "instagram_url": "https://instagram.com",
                    "twitter_url": "https://twitter.com/google",
                },
                "user_preferences": {
                    "is_accepting_payments": True,
                    "minimum_amount": "100",
                },
            },
            format="json",
        )
        assert response.status_code == 200
        assert response.json() == {
            "username": user.username,
            "name": user.name,
            "about": "Hello world! this is me!",
            "avatar": {},
            "cover": {},
            "social_links": {
                "website_url": "https://google.com",
                "youtube_url": "https://youtube.com",
                "facebook_url": "https://fb.com",
                "instagram_url": "https://instagram.com",
                "twitter_url": "https://twitter.com/google",
            },
            "user_preferences": {
                "is_accepting_payments": True,
                "minimum_amount": "100.00",
            },
            "follower_count": 0,
            "subscriber_count": 0,
        }
