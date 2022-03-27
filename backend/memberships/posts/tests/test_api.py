import pytest
from decimal import Decimal
from moneyed import Money, INR
from micawber.exceptions import ProviderException
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

    def test_detail_permissions_on_allowed_tiers_tier_post(
        self, creator_user, api_client
    ):
        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.ALLOWED_TIERS,
            author_user=creator_user,
        )
        post.allowed_tiers.set(creator_user.tiers.all())

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

    def test_detail_allowed_tiers_without_access(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            visibility=Post.Visiblity.ALLOWED_TIERS,
            author_user=creator_user,
        )
        post.allowed_tiers.add(creator_user.tiers.first())

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert not data["can_access"]
        assert not data["can_comment"]

    def test_detail_allowed_tiers_without_access(self, creator_user, user, api_client):
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
            visibility=Post.Visiblity.ALLOWED_TIERS,
            author_user=creator_user,
        )
        post.allowed_tiers.add(gold_tier)

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert not data["can_access"]
        assert not data["can_comment"]

    def test_detail_allowed_tiers_with_access(self, creator_user, user, api_client):
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
            visibility=Post.Visiblity.ALLOWED_TIERS,
            author_user=creator_user,
        )
        post.allowed_tiers.add(gold_tier)

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == post.id
        assert data["can_access"]
        assert data["can_comment"]


class TestPostCreateAPI:
    def test_create_public(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Episode #123 Script",
                "content": {"type": "text", "text": "hello darkness my old friend"},
                "visibility": "public",
            },
        )
        assert response.status_code == 201
        data = response.json()

        assert data["title"] == "Episode #123 Script"
        assert data["slug"] == "episode-123-script"
        assert data["content"] is not None
        assert data["visibility"] == "public"
        assert data["can_access"]
        assert data["can_comment"]

    def test_create_all_members(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Episode #123 Script",
                "content": {"type": "text", "text": "hello darkness my old friend"},
                "visibility": "all_members",
            },
        )
        assert response.status_code == 201
        data = response.json()

        assert data["visibility"] == "all_members"
        assert data["can_access"]
        assert data["can_comment"]

    def test_create_allowed_tiers(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Episode #123 Script",
                "content": {"type": "text", "text": "hello darkness my old friend"},
                "visibility": "allowed_tiers",
                "allowed_tiers": [creator_user.tiers.first().id],
            },
        )
        assert response.status_code == 201
        data = response.json()

        assert data["visibility"] == "allowed_tiers"
        assert data["allowed_tiers"] == [creator_user.tiers.first().id]
        assert data["can_access"]
        assert data["can_comment"]

    def test_create_text(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Episode #123 Script",
                "content": {
                    "type": "text",
                    "text": "hello darkness my old friend",
                },
            },
        )

        assert response.status_code == 201

    def test_create_link_embed(self, creator_user, api_client, mocker):
        request_embed_mock = mocker.Mock(return_value={"foo": "bar"})
        mocker.patch(
            "memberships.posts.models.bootstrap_oembed",
        ).return_value.request = request_embed_mock

        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Youtube",
                "content": {
                    "type": "link",
                    "link": "https://youtube.com",
                },
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"]["link"] == "https://youtube.com"
        assert data["content"]["link_embed"] == {"foo": "bar"}
        request_embed_mock.assert_called_with("https://youtube.com")

    def test_create_link_og(self, creator_user, api_client, mocker):
        # mock oembed to treat this URL as unsupported
        request_embed_mock = mocker.Mock(side_effect=ProviderException)
        mocker.patch(
            "memberships.posts.models.bootstrap_oembed",
        ).return_value.request = request_embed_mock

        mocker.patch(
            "memberships.posts.models.metadata_parser.MetadataParser",
            return_value=mocker.Mock(metadata={"og": "hello", "page": "world"}),
        )

        api_client.force_authenticate(creator_user)
        response = api_client.post(
            "/api/posts/",
            {
                "title": "Google",
                "content": {
                    "type": "link",
                    "link": "https://google.com",
                },
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"]["link"] == "https://google.com"
        assert data["content"]["link_embed"] is None
        assert data["content"]["link_og"] == {"og": "hello", "page": "world"}
        request_embed_mock.assert_called_with("https://google.com")
