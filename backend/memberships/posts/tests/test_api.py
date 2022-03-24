import pytest
from decimal import Decimal
from moneyed import Money, INR
from memberships.posts.models import Post, Content
from memberships.subscriptions.tests.factories import MembershipFactory, TierFactory

pytestmark = pytest.mark.django_db


class TestPostAPIForAnonymousUsers:
    def test_list(self, creator_user, api_client):
        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            author_user=creator_user,
        )

        response = api_client.get("/api/posts/")
        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["id"] == post.id
        assert data["results"][0]["title"] == post.title
        assert data["results"][0]["slug"] == post.slug
        assert data["results"][0]["can_access"]
        assert not data["results"][0]["can_comment"]
        assert data["results"][0]["content"] == {
            "type": "text",
            "text": "I've come to see you again.",
            "image": None,
            "link": "",
            "link_embed": None,
            "link_og": None,
        }

    def test_detail_text(self, creator_user, api_client):
        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert data["title"] == post.title
        assert data["slug"] == post.slug
        assert data["can_access"]
        assert not data["can_comment"]
        assert data["content"] == {
            "type": "text",
            "text": "I've come to see you again.",
            "image": None,
            "link": "",
            "link_embed": None,
            "link_og": None,
        }

    def test_detail_link(self, creator_user, api_client):
        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.LINK,
                link="https://google.com/",
                link_embed={"hello": "world"},
                link_og={"world": "hello"},
            ),
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert data["title"] == post.title
        assert data["slug"] == post.slug
        assert data["can_access"]
        assert not data["can_comment"]
        assert data["content"] == {
            "type": "link",
            "text": "",
            "image": None,
            "link": "https://google.com/",
            "link_embed": {"hello": "world"},
            "link_og": {"world": "hello"},
        }

    def test_detail_permissions_on_member_only_post(self, creator_user, api_client):
        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.ALL_MEMBERS,
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert not data["can_access"]
        assert not data["can_comment"]
        assert data["content"] is None

    def test_detail_permissions_on_minimum_tier_post(self, creator_user, api_client):
        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.MINIMUM_TIER,
            minimum_tier=creator_user.tiers.first(),
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert not data["can_access"]
        assert not data["can_comment"]
        assert data["content"] is None


class TestPostAPIForUser:
    def test_detail_public(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert data["can_access"]
        assert not data["can_comment"]

    def test_detail_all_members_without_access(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.ALL_MEMBERS,
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert not data["can_access"]
        assert not data["can_comment"]

    def test_detail_all_members_with_access(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        MembershipFactory(
            creator_user=creator_user,
            fan_user=user,
            tier=creator_user.tiers.first(),
            is_active=True,
        )

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.ALL_MEMBERS,
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert data["can_access"]
        assert data["can_comment"]

    def test_detail_minimum_tier_without_access(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.MINIMUM_TIER,
            minimum_tier=creator_user.tiers.first(),
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert not data["can_access"]
        assert not data["can_comment"]

    def test_detail_minimum_tier_lesser_tier(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        gold_tier = creator_user.tiers.first()
        silver_tier = TierFactory(
            amount=Money(Decimal("50"), INR), creator_user=creator_user
        )

        MembershipFactory(
            creator_user=creator_user,
            fan_user=user,
            tier=silver_tier,
            is_active=True,
        )

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.MINIMUM_TIER,
            minimum_tier=gold_tier,
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert not data["can_access"]
        assert not data["can_comment"]

    def test_detail_minimum_tier_same_tier(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        gold_tier = creator_user.tiers.first()
        MembershipFactory(
            creator_user=creator_user,
            fan_user=user,
            tier=gold_tier,
            is_active=True,
        )

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.MINIMUM_TIER,
            minimum_tier=gold_tier,
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert data["can_access"]
        assert data["can_comment"]

    def test_detail_minimum_tier_greater_tier(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        gold_tier = creator_user.tiers.first()
        silver_tier = TierFactory(
            amount=Money(Decimal("50"), INR), creator_user=creator_user
        )
        MembershipFactory(
            creator_user=creator_user,
            fan_user=user,
            tier=gold_tier,
            is_active=True,
        )

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.MINIMUM_TIER,
            minimum_tier=silver_tier,
            author_user=creator_user,
        )

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert data["can_access"]
        assert data["can_comment"]
