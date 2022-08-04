from django.http.response import HttpResponse

from fanmo.posts.models import Post
from fanmo.users.models import User
from fanmo.utils.fields import VersatileImageFieldSerializer
from fanmo.utils.helpers import replace_format


def index_view(request, *args, **kwargs):
    return serve_index()


def handle_404(request, *args, **kwargs):
    return serve_index(title="Page not Found", status=404)


def handle_400(request, *args, **kwargs):
    return serve_index(title="Bad Request", status=400)


def handle_500(request, *args, **kwargs):
    return serve_index(title="Internal Server Error", status=404)


def handle_403(request, *args, **kwargs):
    return serve_index(title="Permission Denied", status=404)


def page_view(request, username):
    user = User.objects.filter(
        username=username, is_creator=True, is_active=True
    ).first()
    if not user:
        return serve_index(status=404)

    image_url = None
    if user.cover:
        serializer = VersatileImageFieldSerializer("user_cover")
        serializer._context = {"request": request}
        cover_renditions = serializer.to_representation(user.cover)
        image_url = cover_renditions["social"] if cover_renditions else None

    return serve_index(
        f"{user.display_name} {user.one_liner}",
        f"Support {user.display_name} on Fanmo. Become a member, get access to exclusive content, send donations and much more on Fanmo.",
        image_url,
    )


def post_view(request, post_slug, post_id):
    post = Post.objects.filter(id=post_id, is_published=True).first()
    if not post:
        return serve_index(status=404)

    image_url = None
    if post.author_user.cover:
        serializer = VersatileImageFieldSerializer("user_cover")
        serializer._context = {"request": request}
        cover_renditions = serializer.to_representation(post.author_user.cover)
        image_url = cover_renditions["social"] if cover_renditions else None

    return serve_index(
        f"{post.title} - {post.author_user.display_name}",
        f"Support {post.author_user.display_name} on Fanmo. Become a member, get access to exclusive content, send donations and much more on Fanmo.",
        image_url,
    )


def serve_index(title=None, description=None, image=None, status=200):
    """
    Serve and manipulate 200.html generated by nuxt.
    """
    response_text = open("/var/www/html/200.html").read()
    if title:
        suffixed_title = f"{title.strip()} | Fanmo"
        response_text = replace_format(
            response_text, "<title>%s</title>", suffixed_title
        )
        response_text = replace_format(
            response_text,
            'name="twitter:title" content="%s" data-hid="twitter:title"',
            suffixed_title,
        )
        response_text = replace_format(
            response_text,
            'property="og:title" content="%s" data-hid="og:title"',
            suffixed_title,
        )

    if description:
        response_text = replace_format(
            response_text,
            'name="description" content="%s" data-hid="description"',
            description,
        )
        response_text = replace_format(
            response_text,
            'name="twitter:description" content="%s" data-hid="twitter:description"',
            description,
        )
        response_text = replace_format(
            response_text,
            'property="og:description" content="%s" data-hid="og:description"',
            description,
        )

    if image:
        response_text = replace_format(
            response_text,
            'name="twitter:image" content="%s" data-hid="twitter:image"',
            image,
        )
        response_text = replace_format(
            response_text,
            'property="og:image" content="%s" data-hid="og:image"',
            image,
        )
    return HttpResponse(response_text, "text/html", status=status)
