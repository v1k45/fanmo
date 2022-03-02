import pytest

from memberships.users.models import User

pytestmark = pytest.mark.django_db


class TestAuthenticationFlow:
    def test_register(self, api_client):
        response = api_client.post(
            "/api/auth/register/",
            {
                "name": "Ashok",
                "email": "ashok@gmail.com",
                "password": "s3cr3tP@55w0rd",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json() == {
            "username": "ashok",
            "name": "Ashok",
            "about": "",
            "email": "ashok@gmail.com",
            "avatar": {
                "small": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-150x150-70.jpg",
                "full": "http://testserver/media/__placeholder__/avatar.jpg",
                "thumbnail": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-50x50-70.jpg",
                "medium": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-300x300-70.jpg",
            },
            "cover": {
                "small": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-300x70-70.jpg",
                "medium": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-900x200-70.jpg",
                "full": "http://testserver/media/__placeholder__/cover.jpg",
                "big": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-1800x400-70.jpg",
            },
            "tiers": [],
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "preferences": {"is_accepting_payments": True, "minimum_amount": "10.00"},
            "onboarding": {
                "full_name": "",
                "introduction": "",
                "mobile": "",
                "status": "in_progress",
                "checklist": {
                    "type_selection": False,
                    "email_verification": False,
                    "introduction": False,
                    "payment_setup": False,
                },
            },
            "follower_count": 0,
            "subscriber_count": 0,
            "is_creator": None,
            "is_following": False,
        }
        assert User.objects.get(username="ashok").email == "ashok@gmail.com"

    def test_login(self, user, api_client):
        # test with incorrect login
        response = api_client.post(
            "/api/auth/login/",
            {
                "email": user.email,
                "password": "s3cr3tP@55w0rd",
            },
            format="json",
        )
        assert response.status_code == 400

        user.set_password("s3cr3tP@55w0rd")
        user.save()

        response = api_client.post(
            "/api/auth/login/",
            {
                "email": user.email,
                "password": "s3cr3tP@55w0rd",
            },
            format="json",
        )
        assert response.status_code == 200
        assert response.json() == {
            "username": user.username,
            "name": user.name,
            "about": "",
            "email": user.email,
            "avatar": {
                "small": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-150x150-70.jpg",
                "full": "http://testserver/media/__placeholder__/avatar.jpg",
                "thumbnail": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-50x50-70.jpg",
                "medium": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-300x300-70.jpg",
            },
            "cover": {
                "small": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-300x70-70.jpg",
                "medium": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-900x200-70.jpg",
                "full": "http://testserver/media/__placeholder__/cover.jpg",
                "big": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-1800x400-70.jpg",
            },
            "tiers": [],
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "preferences": {"is_accepting_payments": True, "minimum_amount": "10.00"},
            "onboarding": {
                "full_name": "",
                "introduction": "",
                "mobile": "",
                "status": "in_progress",
                "checklist": {
                    "type_selection": False,
                    "email_verification": False,
                    "introduction": False,
                    "payment_setup": False,
                },
            },
            "follower_count": 0,
            "subscriber_count": 0,
            "is_creator": None,
            "is_following": False,
        }

    def test_me(self, user, api_client):
        api_client.force_authenticate(user)
        response = api_client.get("/api/me/")
        assert response.status_code == 200
        assert response.json() == {
            "username": user.username,
            "name": user.name,
            "about": "",
            "email": user.email,
            "avatar": {
                "small": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-150x150-70.jpg",
                "thumbnail": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-50x50-70.jpg",
                "medium": "http://testserver/media/__sized__/__placeholder__/avatar-crop-c0-5__0-5-300x300-70.jpg",
                "full": "http://testserver/media/__placeholder__/avatar.jpg",
            },
            "cover": {
                "small": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-300x70-70.jpg",
                "full": "http://testserver/media/__placeholder__/cover.jpg",
                "big": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-1800x400-70.jpg",
                "medium": "http://testserver/media/__sized__/__placeholder__/cover-crop-c0-5__0-5-900x200-70.jpg",
            },
            "tiers": [],
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "preferences": {"is_accepting_payments": True, "minimum_amount": "10.00"},
            "onboarding": {
                "full_name": "",
                "introduction": "",
                "mobile": "",
                "status": "in_progress",
                "checklist": {
                    "type_selection": False,
                    "email_verification": False,
                    "introduction": False,
                    "payment_setup": False,
                },
            },
            "follower_count": 0,
            "subscriber_count": 0,
            "is_creator": None,
            "is_following": False,
        }

    def test_email_verification(self, user, api_client, mocker):
        mocker.patch("django_otp.models.random_number_token", return_value="12345")
        api_client.force_authenticate(user)
        assert user.email_verified is False

        response = api_client.post("/api/auth/email/verify/", {}, format="json")
        assert response.status_code == 204

        # test with incorrect otp
        response = api_client.post(
            "/api/auth/email/verify/confirm/", {"code": "00000"}, format="json"
        )
        assert response.status_code == 400
        assert response.json()["code"][0]["code"] == "invalid_otp"
        user.refresh_from_db()
        assert user.email_verified is False

        # test with correct otp
        response = api_client.post(
            "/api/auth/email/verify/confirm/", {"code": "12345"}, format="json"
        )
        assert response.status_code == 204
        user.refresh_from_db()
        assert user.email_verified is True

    @pytest.mark.xfail()
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
                "preferences": {
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
            "email": user.email,
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
            "tiers": [],
        }


class TestOnboardingFlow:
    def test_select_user_type(self, user, api_client):
        api_client.force_authenticate(user)

        # initial case
        response = api_client.get("/api/me/")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_creator"] is None
        assert response_data["onboarding"]["checklist"]["type_selection"] is False

        # become a creator
        response = api_client.patch("/api/me/", {"is_creator": True})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_creator"] is True
        assert response_data["onboarding"]["checklist"]["type_selection"] is True

        # become a supporter from creator
        response = api_client.patch("/api/me/", {"is_creator": False})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_creator"] is False
        assert response_data["onboarding"]["checklist"]["type_selection"] is True

        # cannot reset creator status
        response = api_client.patch("/api/me/", {"is_creator": None})
        assert response.status_code == 400
        response_data = response.json()
        assert "is_creator" in response_data

        # sanity check, not passing is_creator should work too.
        response = api_client.patch("/api/me/", {})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_creator"] is False
        assert response_data["onboarding"]["checklist"]["type_selection"] is True

    def test_creator_cannot_become_supporter_after_approval(self, user, api_client):
        # make it a creator user, who is also approved.
        user.is_creator = True
        user.save()
        user.user_onboarding.is_creator_approved = True
        user.user_onboarding.save()

        api_client.force_authenticate(user)

        # become a creator
        response = api_client.patch("/api/me/", {"is_creator": False})
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["is_creator"][0]["code"] == "manual_intervention_needed"

    def test_email_verification(self, user, api_client):
        api_client.force_authenticate(user)

        # initial case
        response = api_client.get("/api/me/")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["onboarding"]["checklist"]["email_verification"] is False

        # simulate email verification
        user.email_verified = True
        user.save()

        response = api_client.get("/api/me/")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["onboarding"]["checklist"]["email_verification"] is True

    def test_onboarding_details(self, user, api_client):
        api_client.force_authenticate(user)

        # initial case
        response = api_client.get("/api/me/")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["onboarding"]["full_name"] == ""
        assert response_data["onboarding"]["introduction"] == ""
        assert response_data["onboarding"]["mobile"] == ""
        assert response_data["onboarding"]["checklist"]["introduction"] is False

        # become a creator
        response = api_client.patch(
            "/api/me/",
            {"onboarding": {"full_name": "", "introduction": "", "mobile": ""}},
        )
        assert response.status_code == 400
        assert response.json() == {
            "onboarding": {
                "full_name": [
                    {"message": "This field may not be blank.", "code": "blank"}
                ],
                "introduction": [
                    {"message": "This field may not be blank.", "code": "blank"}
                ],
                "mobile": [
                    {"message": "This field may not be blank.", "code": "blank"}
                ],
            }
        }

        # become a supporter from creator
        response = api_client.patch(
            "/api/me/",
            {
                "onboarding": {
                    "full_name": "Ashok Kumar",
                    "introduction": "I am a barbie girl.",
                    "mobile": "1234567890",
                }
            },
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["onboarding"]["full_name"] == "Ashok Kumar"
        assert response_data["onboarding"]["introduction"] == "I am a barbie girl."
        assert response_data["onboarding"]["mobile"] == "1234567890"
        assert response_data["onboarding"]["checklist"]["introduction"] is True

    def test_payment_setup(self, user, api_client):
        api_client.force_authenticate(user)

        # initial case
        response = api_client.get("/api/me/")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["onboarding"]["checklist"]["payment_setup"] is False

        # simulate bank account setup
        user.user_onboarding.is_bank_account_added = True
        user.user_onboarding.save()

        response = api_client.get("/api/me/")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["onboarding"]["checklist"]["payment_setup"] is True

    def test_submit_for_review(self, user, api_client):
        api_client.force_authenticate(user)

        # onboarding in progress
        response = api_client.get("/api/me/")
        assert response.status_code == 200
        assert response.json()["onboarding"]["status"] == "in_progress"

        # attempt without creator type selected
        response = api_client.patch(
            "/api/me/", {"onboarding": {"submit_for_review": True}}
        )
        assert response.status_code == 400
        assert (
            response.json()["onboarding"]["submit_for_review"][0]["code"]
            == "creator_type_required"
        )

        user.is_creator = True
        user.save()

        # attempt without email verification
        response = api_client.patch(
            "/api/me/", {"onboarding": {"submit_for_review": True}}
        )
        assert response.status_code == 400
        assert (
            response.json()["onboarding"]["submit_for_review"][0]["code"]
            == "email_verification_required"
        )

        user.email_verified = True
        user.save()

        # attempt without payment setup
        response = api_client.patch(
            "/api/me/", {"onboarding": {"submit_for_review": True}}
        )
        assert response.status_code == 400
        assert (
            response.json()["onboarding"]["submit_for_review"][0]["code"]
            == "payment_setup_required"
        )

        user.user_onboarding.is_bank_account_added = True
        user.user_onboarding.save()

        # attempt with all checks completed
        response = api_client.patch(
            "/api/me/", {"onboarding": {"submit_for_review": True}}
        )
        assert response.status_code == 200
        assert response.json()["onboarding"]["status"] == "submitted"

    def test_onboarding_details_becomes_read_only_once_submitted(
        self, user, api_client
    ):
        api_client.force_authenticate(user)

        user.user_onboarding.full_name = "Ashok Kumar"
        user.user_onboarding.status = "submitted"
        user.user_onboarding.save()

        # full name is not updated
        response = api_client.patch(
            "/api/me/", {"onboarding": {"full_name": "Anjali Mishra"}}
        )
        assert response.status_code == 200
        assert response.json()["onboarding"]["full_name"] == "Ashok Kumar"
