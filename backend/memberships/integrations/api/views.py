from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialConnectView

from memberships.integrations.oauth_adapters import DiscordServerOAuth2Adapter, DiscordUserOAuth2Adapter


class DiscordUserConnectView(SocialConnectView):
    adapter_class = DiscordUserOAuth2Adapter
    client_class = OAuth2Client

    def get_response_serializer(self):
        # return discord user?
        return super().get_response_serializer()


class DiscordServerConnectView(SocialConnectView):
    adapter_class = DiscordServerOAuth2Adapter
    client_class = OAuth2Client

    def get_response_serializer(self):
        # return discord server?
        return super().get_response_serializer()
