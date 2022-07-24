from decimal import Decimal

import pytest
from django.conf import settings
from moneyed import INR, Money

from fanmo.core.models import NotificationType
from fanmo.donations.models import Donation
from fanmo.posts.models import Comment, Content, Post
from fanmo.users.models import CreatorActivity, User, UserPreference

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
            "display_name": "Ashok",
            "one_liner": "",
            "about": "",
            "email": "ashok@gmail.com",
            "avatar": None,
            "cover": None,
            "tiers": [],
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "preferences": {
                "is_accepting_payments": True,
                "minimum_amount": "10.00",
                "donation_description": "",
                "thank_you_message": settings.DEFAULT_THANK_YOU_MESSAGE,
                "notify_following_posts": True,
                "notify_comment_replies": True,
                "notify_post_comments": True,
                "notify_donations": True,
                "notify_memberships": True,
                "notify_marketing": True,
            },
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
            "is_member": False,
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
            "display_name": user.name,
            "one_liner": "",
            "about": "",
            "email": user.email,
            "avatar": None,
            "cover": None,
            "tiers": [],
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "preferences": {
                "is_accepting_payments": True,
                "minimum_amount": "10.00",
                "donation_description": "",
                "thank_you_message": settings.DEFAULT_THANK_YOU_MESSAGE,
                "notify_following_posts": True,
                "notify_comment_replies": True,
                "notify_post_comments": True,
                "notify_donations": True,
                "notify_memberships": True,
                "notify_marketing": True,
            },
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
            "is_member": False,
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


class TestMeAPI:
    def test_me(self, user, api_client):
        api_client.force_authenticate(user)
        response = api_client.get("/api/me/")
        assert response.status_code == 200
        assert response.json() == {
            "username": user.username,
            "name": user.name,
            "display_name": user.name,
            "one_liner": "",
            "about": "",
            "email": user.email,
            "avatar": None,
            "cover": None,
            "tiers": [],
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "preferences": {
                "is_accepting_payments": True,
                "minimum_amount": "10.00",
                "donation_description": "",
                "thank_you_message": settings.DEFAULT_THANK_YOU_MESSAGE,
                "notify_following_posts": True,
                "notify_comment_replies": True,
                "notify_post_comments": True,
                "notify_donations": True,
                "notify_memberships": True,
                "notify_marketing": True,
            },
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
            "is_member": False,
        }

    def test_update(self, user, api_client):
        api_client.force_authenticate(user)
        response = api_client.patch(
            "/api/me/",
            {
                "one_liner": "is creating podcast",
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
                    "donation_description": "Hello world!",
                    "thank_you_message": "thanksbro",
                    "notify_following_posts": True,
                    "notify_comment_replies": False,
                    "notify_post_comments": True,
                    "notify_donations": False,
                    "notify_memberships": True,
                    "notify_marketing": False,
                },
            },
            format="json",
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["one_liner"] == "is creating podcast"
        assert response_data["about"] == "Hello world! this is me!"
        assert response_data["social_links"] == {
            "website_url": "https://google.com",
            "youtube_url": "https://youtube.com",
            "facebook_url": "https://fb.com",
            "instagram_url": "https://instagram.com",
            "twitter_url": "https://twitter.com/google",
        }
        assert response_data["preferences"] == {
            "is_accepting_payments": True,
            "minimum_amount": "100.00",
            "donation_description": "Hello world!",
            "thank_you_message": "thanksbro",
            "notify_following_posts": True,
            "notify_comment_replies": False,
            "notify_post_comments": True,
            "notify_donations": False,
            "notify_memberships": True,
            "notify_marketing": False,
        }

    def test_update_about_xss(self, user, api_client):
        api_client.force_authenticate(user)

        response = api_client.patch(
            "/api/me/",
            {
                "about": '<b>Hello</b><strong>world</strong>! <a title="xss" href="javascript:alert(0);">click me</a>'
            },
        )
        assert response.status_code == 200
        assert (
            response.json()["about"]
            == "<b>Hello</b><strong>world</strong>! <a>click me</a>"
        )

    def test_update_username_reserved_names(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)
        response = api_client.patch("/api/me/", {"username": "login"})
        assert response.status_code == 400
        assert response.json()["username"][0]["code"] == "already_taken"

    def test_update_username_as_a_fan(self, user, api_client):
        api_client.force_authenticate(user)
        response = api_client.patch("/api/me/", {"username": "yeahbaby"})
        assert response.status_code == 400
        assert response.json()["username"][0]["code"] == "invalid"


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


class TestUserAPI:
    def test_retrieve(self, api_client, creator_user):
        tier = creator_user.tiers.first()
        response = api_client.get(f"/api/users/{creator_user.username}/")
        assert response.status_code == 200
        assert response.json() == {
            "username": creator_user.username,
            "name": creator_user.name,
            "display_name": creator_user.name,
            "one_liner": "",
            "about": "",
            "avatar": None,
            "cover": None,
            "tiers": [
                {
                    "id": tier.id,
                    "name": tier.name,
                    "description": "",
                    "amount": "100.00",
                    "cover": None,
                    "cover_background_style": "contain",
                    "benefits": ["Membership!"],
                    "is_recommended": False,
                }
            ],
            "social_links": {
                "website_url": "",
                "youtube_url": "",
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": "",
            },
            "preferences": {
                "is_accepting_payments": True,
                "minimum_amount": "10.00",
                "donation_description": "",
                "thank_you_message": settings.DEFAULT_THANK_YOU_MESSAGE,
            },
            "is_creator": True,
            "follower_count": 0,
            "is_following": False,
            "is_member": False,
        }

    def test_follow(self, api_client, creator_user, user):
        api_client.force_authenticate(user)
        response = api_client.post(f"/api/users/{creator_user.username}/follow/")
        assert response.status_code == 200
        assert response.json()["is_following"]

    def test_unfollow(self, api_client, creator_user, user):
        api_client.force_authenticate(user)
        response = api_client.post(f"/api/users/{creator_user.username}/unfollow/")
        assert response.status_code == 200
        assert not response.json()["is_following"]

    def test_membership(self, api_client, active_membership):
        api_client.force_authenticate(active_membership.fan_user)
        response = api_client.get(
            f"/api/users/{active_membership.creator_user.username}/"
        )
        assert response.status_code == 200
        assert response.json()["is_member"]


class TestActivitiesAPI:
    def test_list(self, creator_user, user, active_membership, api_client):

        CreatorActivity.objects.create(
            type=CreatorActivity.Type.MEMBERSHIP_UPDATE,
            message="Foo changed Bar to Bam",
            data={"foo": {"bar": "bam"}},
            membership=active_membership,
            creator_user=creator_user,
            fan_user=user,
        )

        donation = Donation.objects.create(
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("100"), INR),
            status=Donation.Status.SUCCESSFUL,
        )
        CreatorActivity.objects.create(
            type=CreatorActivity.Type.DONATION,
            message="Foo donated 100",
            data={"foo": {"bar": "bam"}},
            donation=donation,
            creator_user=creator_user,
            fan_user=user,
        )

        comment = Comment.objects.create(
            post=Post.objects.create(
                author_user=creator_user,
                title="Sum ting wong",
                content=Content.objects.create(type=Content.Type.TEXT),
            ),
            author_user=user,
            body="ho lee fuk",
        )
        CreatorActivity.objects.create(
            type=CreatorActivity.Type.COMMENT,
            message="Foo commented on Sum ting wong",
            comment=comment,
            creator_user=creator_user,
            fan_user=user,
        )

        api_client.force_authenticate(creator_user)

        response = api_client.get("/api/activities/")
        response_data = response.json()

        assert response.status_code == 200
        # one extra because an activity is created when membership is activated.
        assert response_data["count"] == 4

        assert response_data["results"][0]["type"] == CreatorActivity.Type.COMMENT
        assert response_data["results"][0]["data"] == {}
        assert response_data["results"][0]["comment"]["id"] == comment.id
        assert response_data["results"][0]["fan_user"]["username"] == user.username

        assert response_data["results"][1]["type"] == CreatorActivity.Type.DONATION
        assert response_data["results"][1]["data"] == {"foo": {"bar": "bam"}}
        assert response_data["results"][1]["donation"]["id"] == donation.id
        assert response_data["results"][1]["fan_user"]["username"] == user.username

        assert (
            response_data["results"][2]["type"]
            == CreatorActivity.Type.MEMBERSHIP_UPDATE
        )
        assert response_data["results"][2]["data"] == {"foo": {"bar": "bam"}}
        assert response_data["results"][2]["membership"]["id"] == active_membership.id
        assert response_data["results"][2]["fan_user"]["username"] == user.username

        assert (
            response_data["results"][3]["type"] == CreatorActivity.Type.NEW_MEMBERSHIP
        )
        assert response_data["results"][3]["data"] == {
            "tier": {
                "id": active_membership.tier.id,
                "name": active_membership.tier.name,
            }
        }
        assert (
            response_data["results"][3]["message"]
            == f"{active_membership.fan_user.display_name} joined {active_membership.tier.name}."
        )
        assert response_data["results"][3]["membership"]["id"] == active_membership.id
        assert response_data["results"][3]["fan_user"]["username"] == user.username


class TestNotificationSettings:
    all_notification_types = [*NotificationType.values]
    whitelisted_notification_types = all_notification_types
    whitelisted_notification_types.remove(NotificationType.PASSWORD_CHANGE)

    @pytest.mark.parametrize("notification_type", NotificationType.values)
    def test_can_send_email_notification_all_allowed(self, user, notification_type):
        assert user.user_preferences.can_send_email_notification(notification_type)

    @pytest.mark.parametrize("notification_type", whitelisted_notification_types)
    def test_can_send_email_notification_disallow_allowed(
        self, user, notification_type
    ):
        prefs: UserPreference = user.user_preferences
        prefs.notify_comment_replies = False
        prefs.notify_post_comments = False
        prefs.notify_following_posts = False
        prefs.notify_donations = False
        prefs.notify_memberships = False
        prefs.notify_marketing = False
        prefs.save()

        assert not prefs.can_send_email_notification(notification_type)
