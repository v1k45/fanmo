from whitenoise.middleware import WhiteNoiseMiddleware
from whitenoise.responders import Redirect as WhitenoiseRedirect


class StaticServerMiddleware(WhiteNoiseMiddleware):
    """
    Extension over whitenoise to forward URL params while redirecting to auth callback index page.

    This is needed because nuxt-auth strips trailing slash while building OAuth Callback URL and
    whitenoise strips the URL parameter when redirecting to URL with traiing slash.
    """

    @staticmethod
    def serve(static_file, request):
        if isinstance(static_file, WhitenoiseRedirect) and "callback" in request.path:
            # do not serve auth callback redirect from static server.
            # static file server caches the URL along with parameters, which makes OAuth break because of HPP
            # returning None will make django handle the redirect and then the actual request will come back to whitenoise again.
            #
            # auth/callback?code=123 - redir -> auth/callback/?code=123 (django)
            # auth/callback/?code=123 - serve -> white noise
            return None
        return WhiteNoiseMiddleware.serve(static_file, request)
