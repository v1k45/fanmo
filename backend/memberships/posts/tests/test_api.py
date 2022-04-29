import pytest
from decimal import Decimal
from moneyed import Money, INR
from micawber.exceptions import ProviderException
from memberships.posts.models import Post, Content, Comment, Reaction
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
        assert data["results"][0]["minimum_tier"]["id"] == creator_user.tiers.first().id
        assert data["results"][0]["content"] == {
            "type": "text",
            "text": "I've come to see you again.",
            "image": None,
            "files": [],
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
        assert data["minimum_tier"]["id"] == creator_user.tiers.first().id
        assert data["content"] == {
            "type": "text",
            "text": "I've come to see you again.",
            "image": None,
            "files": [],
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
        assert data["minimum_tier"]["id"] == creator_user.tiers.first().id
        assert data["content"] == {
            "type": "link",
            "text": "",
            "image": None,
            "files": [],
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
        assert data["minimum_tier"]["id"] == creator_user.tiers.first().id
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
        assert data["minimum_tier"]["id"] == creator_user.tiers.first().id
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
        assert data["minimum_tier"]["id"] == creator_user.tiers.first().id

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
        assert data["minimum_tier"]["id"] == creator_user.tiers.first().id

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
        assert data["minimum_tier"] is None

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
        assert data["minimum_tier"]["id"] == creator_user.tiers.first().id

    def test_detail_allowed_tiers_without_specific_access(
        self, creator_user, user, api_client
    ):
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
        assert data["minimum_tier"]["id"] == gold_tier.id

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
        assert data["minimum_tier"] is None

    def test_detail_stats(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            author_user=creator_user,
        )
        # create comments
        Comment.objects.create(post=post, body="hello", author_user=creator_user)
        Comment.objects.create(post=post, body="world", author_user=creator_user)
        Comment.objects.create(
            post=post, body="word", author_user=creator_user, is_published=False
        )

        # create reactions
        Reaction.objects.create(post=post, emoji=Reaction.Emoji.HEART, author_user=user)

        response = api_client.get(f"/api/posts/{post.id}/")
        assert response.status_code == 200
        data = response.json()["stats"]

        assert data["comment_count"] == 2
        assert data["reactions"] == [
            {
                "count": 1,
                "is_reacted": True,
                "emoji": Reaction.Emoji.HEART.value,
            }
        ]

    def test_add_reactions(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            author_user=creator_user,
        )

        response = api_client.post(
            f"/api/posts/{post.id}/reactions/",
            {
                "action": "add",
                "emoji": "heart",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reactions"] == [
            {
                "count": 1,
                "is_reacted": True,
                "emoji": Reaction.Emoji.HEART.value,
            }
        ]

    def test_remove_reactions(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            author_user=creator_user,
        )
        Reaction.objects.create(author_user=user, emoji=Reaction.Emoji.HEART, post=post)

        response = api_client.post(
            f"/api/posts/{post.id}/reactions/", {"action": "remove", "emoji": "heart"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reactions"] == []


class TestPostCrudAPI:
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
                "allowed_tiers_ids": [creator_user.tiers.first().id],
            },
        )
        assert response.status_code == 201
        data = response.json()

        assert data["visibility"] == "allowed_tiers"
        assert data["allowed_tiers"][0]["id"] == creator_user.tiers.first().id
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
            return_value=mocker.Mock(
                metadata={"og": "hello", "page": "world", "meta": {"foo": "bar"}}
            ),
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
        assert data["content"]["link_og"] == {
            "og": "hello",
            "page": "world",
            "meta": {"foo": "bar"},
        }
        request_embed_mock.assert_called_with("https://google.com")

    def test_create_images(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Episode #123 Script",
                "content": {
                    "type": "images",
                    "text": "hello darkness my old friend",
                    "files": [
                        {
                            # green.png
                            "type": "image",
                            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdj0J0Y+B8ABA0CD2aRx64AAAAASUVORK5CYII=",
                        },
                        {
                            # orange.png
                            "type": "image",
                            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjuD8x8D8ABtUCwenGWNgAAAAASUVORK5CYII=",
                        },
                    ],
                },
            },
        )

        assert response.status_code == 201
        response_data = response.json()
        files_data = response_data["content"]["files"]

        assert len(files_data) == 2
        assert files_data[0]["type"] == "image"
        assert files_data[0]["image"] is not None
        assert files_data[0]["attachment"] is None

        assert files_data[1]["type"] == "image"
        assert files_data[1]["image"] is not None
        assert files_data[1]["attachment"] is None

    def test_delete(self, api_client, creator_user, user):
        post = Post.objects.create(
            visibility=Post.Visiblity.PUBLIC,
            author_user=creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )

        api_client.force_authenticate(user)
        response = api_client.delete(f"/api/posts/{post.id}/")
        assert response.status_code == 404

        api_client.force_authenticate(creator_user)
        response = api_client.delete(f"/api/posts/{post.id}/")
        assert response.status_code == 204

        response = api_client.delete(f"/api/posts/{post.id}/")
        assert response.status_code == 404

    def test_create_text_error(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Episode #123 Script",
                "content": {
                    "type": "text",
                    "text": "",
                },
            },
        )

        assert response.status_code == 400
        assert response.json()["content"]["text"][0]["code"] == "required"

    def test_create_link_error(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Episode #123 Script",
                "content": {
                    "type": "link",
                    "link": "",
                },
            },
        )

        assert response.status_code == 400
        assert response.json()["content"]["link"][0]["code"] == "required"

    def test_create_files_error(self, creator_user, api_client):
        api_client.force_authenticate(creator_user)

        response = api_client.post(
            "/api/posts/",
            {
                "title": "Episode #123 Script",
                "content": {
                    "type": "images",
                },
            },
        )

        assert response.status_code == 400
        assert response.json()["content"]["files"][0]["code"] == "required"

    def test_link_preview(self, creator_user, mocker, api_client):
        request_embed_mock = mocker.Mock(return_value={"foo": "bar"})
        mocker.patch(
            "memberships.posts.models.bootstrap_oembed",
        ).return_value.request = request_embed_mock

        mocker.patch(
            "memberships.posts.models.metadata_parser.MetadataParser",
            return_value=mocker.Mock(
                metadata={"og": "hello", "page": "world", "meta": {"foo": "bar"}}
            ),
        )

        api_client.force_authenticate(creator_user)
        response = api_client.post(
            "/api/posts/link_preview/",
            {"link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "link_og": {"og": "hello", "page": "world", "meta": {"foo": "bar"}},
            "link_embed": {"foo": "bar"},
        }


class TestCommentAPI:
    def test_list_without_post_id(self, api_client):
        response = api_client.get("/api/comments/")
        assert response.status_code == 400

    def test_list_with_post_id(self, api_client):
        response = api_client.get("/api/comments/")
        assert response.status_code == 400

    def test_create_comment_anonymous(self, api_client, creator_user):
        post = Post.objects.create(
            visibility=Post.Visiblity.PUBLIC,
            author_user=creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )

        response = api_client.post(
            "/api/comments/",
            {
                "post_id": post.id,
                "body": "nice pic, deer",
            },
        )
        assert response.status_code == 403

    def test_create_comment_non_member(self, api_client, creator_user, user):
        post = Post.objects.create(
            visibility=Post.Visiblity.PUBLIC,
            author_user=creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )

        api_client.force_authenticate(user)
        response = api_client.post(
            "/api/comments/",
            {
                "post_id": post.id,
                "body": "nice pic, deer",
            },
        )
        assert response.status_code == 400
        assert response.json()["post_id"][0]["code"] == "permission_denied"

    def test_create_comment_by_author(self, api_client, creator_user):
        post = Post.objects.create(
            visibility=Post.Visiblity.PUBLIC,
            author_user=creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )

        api_client.force_authenticate(creator_user)
        response = api_client.post(
            "/api/comments/",
            {
                "post_id": post.id,
                "body": "nice pic, deer",
            },
        )
        assert response.status_code == 201
        response_data = response.json()

        assert response_data["body"] == "nice pic, deer"
        assert response_data["author_user"]["username"] == creator_user.username

    def test_create_comment_member_on_public_post(self, api_client, active_membership):
        post = Post.objects.create(
            visibility=Post.Visiblity.PUBLIC,
            author_user=active_membership.creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )

        api_client.force_authenticate(active_membership.fan_user)
        response = api_client.post(
            "/api/comments/",
            {
                "post_id": post.id,
                "body": "nice pic, deer",
            },
        )
        assert response.status_code == 201
        response_data = response.json()

        assert response_data["body"] == "nice pic, deer"
        assert (
            response_data["author_user"]["username"]
            == active_membership.fan_user.username
        )

    def test_create_comment_member_on_members_only_post(
        self, api_client, active_membership
    ):
        post = Post.objects.create(
            visibility=Post.Visiblity.ALL_MEMBERS,
            author_user=active_membership.creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )

        api_client.force_authenticate(active_membership.fan_user)
        response = api_client.post(
            "/api/comments/",
            {
                "post_id": post.id,
                "body": "nice pic, deer",
            },
        )
        assert response.status_code == 201
        response_data = response.json()

        assert response_data["body"] == "nice pic, deer"
        assert (
            response_data["author_user"]["username"]
            == active_membership.fan_user.username
        )

    def test_create_comment_member_on_allowed_tiers_only_post(
        self, api_client, active_membership
    ):
        post = Post.objects.create(
            visibility=Post.Visiblity.ALLOWED_TIERS,
            author_user=active_membership.creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )
        post.allowed_tiers.add(active_membership.tier)

        api_client.force_authenticate(active_membership.fan_user)
        response = api_client.post(
            "/api/comments/",
            {
                "post_id": post.id,
                "body": "nice pic, deer",
            },
        )
        assert response.status_code == 201
        response_data = response.json()

        assert response_data["body"] == "nice pic, deer"
        assert (
            response_data["author_user"]["username"]
            == active_membership.fan_user.username
        )

    def test_create_comment_member_on_disallowed_tiers_only_post(
        self, api_client, membership_with_scheduled_change
    ):
        post = Post.objects.create(
            visibility=Post.Visiblity.ALLOWED_TIERS,
            author_user=membership_with_scheduled_change.creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )
        post.allowed_tiers.add(
            membership_with_scheduled_change.scheduled_subscription.plan.tier
        )

        api_client.force_authenticate(membership_with_scheduled_change.fan_user)
        response = api_client.post(
            "/api/comments/",
            {
                "post_id": post.id,
                "body": "nice pic, deer",
            },
        )
        assert response.status_code == 400
        assert response.json()["post_id"][0]["code"] == "permission_denied"

    def test_create_comment_reply_member_on_public_post(
        self, api_client, active_membership
    ):
        post = Post.objects.create(
            visibility=Post.Visiblity.PUBLIC,
            author_user=active_membership.creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )
        comment = Comment.objects.create(
            post=post, author_user=active_membership.creator_user, body="hi"
        )

        api_client.force_authenticate(active_membership.fan_user)
        response = api_client.post(
            "/api/comments/",
            {
                "post_id": post.id,
                "parent_id": comment.id,
                "body": "nice pic, deer",
            },
        )
        assert response.status_code == 201
        response_data = response.json()

        assert response_data["body"] == "nice pic, deer"
        assert (
            response_data["author_user"]["username"]
            == active_membership.fan_user.username
        )

    def test_delete_as_creator(self, api_client, active_membership):
        post = Post.objects.create(
            visibility=Post.Visiblity.PUBLIC,
            author_user=active_membership.creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )
        creator_comment = Comment.objects.create(
            post=post, author_user=active_membership.creator_user, body="hi"
        )
        fan_comment = Comment.objects.create(
            post=post,
            author_user=active_membership.fan_user,
            body="hi",
            parent=creator_comment,
        )

        api_client.force_authenticate(active_membership.creator_user)
        response = api_client.delete(f"/api/comments/{creator_comment.id}/")
        assert response.status_code == 204

        # reply also gets unpublished
        response = api_client.delete(f"/api/comments/{fan_comment.id}/")
        assert response.status_code == 404

    def test_delete_as_fan(self, api_client, active_membership):
        post = Post.objects.create(
            visibility=Post.Visiblity.PUBLIC,
            author_user=active_membership.creator_user,
            content=Content.objects.create(type=Content.Type.TEXT, text="Hello world!"),
        )
        creator_comment = Comment.objects.create(
            post=post, author_user=active_membership.creator_user, body="hi"
        )
        fan_comment = Comment.objects.create(
            post=post,
            author_user=active_membership.fan_user,
            body="hi",
            parent=creator_comment,
        )

        api_client.force_authenticate(active_membership.fan_user)
        response = api_client.delete(f"/api/comments/{creator_comment.id}/")
        assert response.status_code == 404

        response = api_client.delete(f"/api/comments/{fan_comment.id}/")
        assert response.status_code == 204

    def test_add_reactions(self, creator_user, user, api_client):
        api_client.force_authenticate(user)

        post = Post.objects.create(
            title="Hello Darkness",
            content=Content.objects.create(
                type=Content.Type.TEXT, text="I've come to see you again."
            ),
            author_user=creator_user,
        )
        comment = Comment.objects.create(post=post, author_user=creator_user, body="hi")

        response = api_client.post(
            f"/api/comments/{comment.id}/reactions/",
            {
                "action": "add",
                "emoji": "heart",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reactions"] == [
            {
                "count": 1,
                "is_reacted": True,
                "emoji": Reaction.Emoji.HEART.value,
            }
        ]
