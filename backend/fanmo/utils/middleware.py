from whitenoise.middleware import WhiteNoiseFileResponse, WhiteNoiseMiddleware
from whitenoise.responders import Redirect as WhitenoiseRedirect


class Redirect(WhitenoiseRedirect):
    def get_response(self, method, request_headers, request_params=None):
        if request_params:
            for idx, (header, value) in enumerate(self.response.headers):
                if header == "Location":
                    self.response.headers[idx] = (
                        header,
                        f"{value}?{request_params.urlencode()}",
                    )
        return self.response


class StaticServerMiddleware(WhiteNoiseMiddleware):
    """
    Extension over whitenoise to forward URL params while redirecting to index page.

    This is needed because nuxt-auth strips trailing slash while building OAuth Callback URL and
    whitenoise strips the URL parameter when redirecting to URL with traiing slash.
    """

    def redirect(self, from_url, to_url):
        """
        Copied verbatim from whitenoise, only difference is that this uses custom redirect responder.
        """
        if to_url == from_url + "/":
            relative_url = from_url.split("/")[-1] + "/"
        elif from_url == to_url + self.index_file:
            relative_url = "./"
        else:
            raise ValueError(f"Cannot handle redirect: {from_url} > {to_url}")
        if self.max_age is not None:
            headers = {"Cache-Control": f"max-age={self.max_age}, public"}
        else:
            headers = {}
        return Redirect(relative_url, headers=headers)

    @staticmethod
    def serve(static_file, request):
        """
        Copied verbatim from whitenoise, only forwards URL params to redirect responder.
        """
        if isinstance(static_file, Redirect):
            response = static_file.get_response(
                request.method, request.META, request.GET
            )
        else:
            response = static_file.get_response(request.method, request.META)
        status = int(response.status)
        http_response = WhiteNoiseFileResponse(response.file or (), status=status)
        # Remove default content-type
        del http_response["content-type"]
        for key, value in response.headers:
            http_response[key] = value
        return http_response
