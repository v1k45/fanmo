from textwrap import wrap

from django.conf import settings
from django.core.files.base import ContentFile
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from fanmo.posts.models import Content, Post


def generate_page_summary(creator_user):
    """
    Generate page summary image file.
    """
    with Image(width=1200, height=630, background=Color("#FFF")) as canvas:
        draw_background(canvas, creator_user.cover)
        # avatar image slightly above the center
        draw_avatar(canvas, creator_user, 500, 85)

        # creator name and oneliner below the avatar image
        draw_text(canvas, creator_user.display_name, x=0, y=10, bold=True, font_size=48)
        if creator_user.one_liner:
            draw_text(canvas, creator_user.one_liner, x=0, y=50, font_size=28)

        # page link with callout below creator details
        draw_text(
            canvas,
            "Support me by becoming a member or sending a tip",
            x=0,
            y=130,
            bold=True,
            font_size=24,
        )
        draw_text(canvas, creator_user.page_link, x=0, y=160, font_size=20)

        draw_logo(canvas)

        return ContentFile(canvas.make_blob("jpeg"))


def generate_post_summary(post):
    """
    Generate profile summary image file.
    """
    with Image(width=1200, height=630, background=Color("#FFF")) as canvas:

        if post.content.type == Content.Type.IMAGES:
            draw_background(canvas, post.content.files.first().image, blur=30)
        else:
            draw_background(canvas, post.author_user.cover)

        # avatar image on bottom left
        draw_avatar(canvas, post.author_user, 50, 400)

        # post title and callout in center
        draw_text(
            canvas,
            "Become a member on Fanmo to unlock this post",
            x=0,
            y=100,
            font_size=28,
            gravity="north",
        )
        draw_text(
            canvas,
            post.title,
            x=0,
            y=200,
            bold=True,
            font_size=48,
            gravity="north",
            roi_height=250,
        )

        # user info next to profile image drawn in bottom left
        draw_text(
            canvas,
            post.author_user.display_name,
            x=280,
            y=150,
            bold=True,
            font_size=48,
            gravity="south_west",
        )
        if post.author_user.one_liner:
            draw_text(
                canvas,
                post.author_user.one_liner,
                x=280,
                y=120,
                font_size=28,
                gravity="south_west",
            )
        draw_text(
            canvas,
            post.author_user.page_link,
            x=280,
            y=80,
            font_size=20,
            gravity="south_west",
        )

        draw_logo(canvas)

        return ContentFile(canvas.make_blob("jpeg"))


def draw_text(
    canvas,
    text,
    x=0,
    y=0,
    bold=False,
    font_size=24,
    gravity="center",
    roi_width=1000,
    roi_height=150,
):
    """
    Draw text over image canvas.

    Parameters
    ----------
    canvas: Image
    text: str
    x: int
        X co-oridate from the supplied gravity
    y: int
        Y co-oridate from the supplied gravity
    gravity: str
        Base position of drawing
    roi_width: int
        Region of Interest for wrapping text width
    roi_height: int
        Region of Interest for wrapping text height
    """
    with Drawing() as draw:
        draw.font = str(
            settings.RESOURCES_DIR / ("WorkSans-Bold.ttf" if bold else "WorkSans.ttf")
        )
        draw.font_size = font_size
        draw.fill_color = Color("#FFF")
        draw.gravity = gravity
        draw.text_antialias = True
        draw.stroke_width = 1
        draw.text(x, y, word_wrap(canvas, draw, text, roi_width, roi_height))
        draw(canvas)


def draw_background(canvas, cover, blur=5):
    """
    Draw cover image and a grey overlay on a blank canvas.
    """
    if cover:
        with Image(file=cover.file) as cover_image:
            cover_image.auto_orient()
            cover_image.transform(resize="1200x630^")
            cover_image.extent(1200, 630, gravity="center")
            cover_image.blur(sigma=blur)
            canvas.composite(cover_image)

    with Color("rgba(43, 43, 43, 0.7)") as overlay_color:
        with Image(
            width=canvas.width, height=canvas.height, background=overlay_color
        ) as overlay_image:
            canvas.composite(overlay_image)


def draw_avatar(canvas, creator_user, left=0, top=0):
    """
    Draw avatar image on a given canvas

    Parameters
    ----------
    canvas: Image
    creator_user: User
    left: int
        left position/co-ordinate for drawing
    top: int
        top position/co-ordinate for drawing
    """
    avatar_image = (
        Image(file=creator_user.avatar.file)
        if creator_user.avatar
        else Image(filename=str(settings.RESOURCES_DIR / "icon.png"))
    )
    with avatar_image:
        avatar_image.auto_orient()
        avatar_image.transform(resize="250x250^")
        avatar_image.extent(250, 250, gravity="center")
        with Image(
            filename=str(settings.RESOURCES_DIR / "avatar_mask.png")
        ) as mask_image:
            avatar_image.composite(mask_image, operator="copy_opacity")
        avatar_image.resize(200, 200)
        canvas.composite(avatar_image, left, top)


def draw_logo(canvas):
    """
    Draw fanmo logo on the bottom right of the canvas.
    """
    with Image(filename=str(settings.RESOURCES_DIR / "logo.png")) as logo_image:
        logo_image.transform(resize="180x34^")
        canvas.composite(logo_image, 970, 560)


def word_wrap(image, ctx, text, roi_width, roi_height):
    """
    Copied verbatim from Wand documentation.

    Break long text to multiple lines, and reduce point size until all text fits within a bounding box.
    """
    mutable_message = text
    iteration_attempts = 100

    def eval_metrics(txt):
        """Quick helper function to calculate width/height of text."""
        metrics = ctx.get_font_metrics(image, txt, True)
        return (metrics.text_width, metrics.text_height)

    while ctx.font_size > 0 and iteration_attempts:
        iteration_attempts -= 1
        width, height = eval_metrics(mutable_message)
        if height > roi_height:
            ctx.font_size -= 0.75  # Reduce pointsize
            mutable_message = text  # Restore original text
        elif width > roi_width:
            columns = len(mutable_message)
            while columns > 0:
                columns -= 1
                mutable_message = "\n".join(wrap(mutable_message, columns))
                wrapped_width, _ = eval_metrics(mutable_message)
                if wrapped_width <= roi_width:
                    break
            if columns < 1:
                ctx.font_size -= 0.75  # Reduce pointsize
                mutable_message = text  # Restore original text
        else:
            break
    # in theory this should never happen because the text supplied
    # to it is never expected to be so large.
    if iteration_attempts < 1:
        raise RuntimeError("Unable to calculate word_wrap for " + text)
    return mutable_message
