import requests
from django.conf import settings


class DiscordAPI:
    base_url = "https://discord.com/api/v10"
    client_id = settings.SOCIALACCOUNT_PROVIDERS["discord_server"]["APP"]["client_id"]
    client_secret = settings.SOCIALACCOUNT_PROVIDERS["discord_server"]["APP"]["secret"]
    server_permissions = "268435459"
    bot_access_token = settings.SOCIALACCOUNT_PROVIDERS["discord_server"]["APP"][
        "access_token"
    ]

    def get_token(self, code, redirect_uri):
        endpoint = self.base_url + "/oauth2/token"
        response = requests.post(
            endpoint,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_user(self, access_token):
        endpoint = self.base_url + "/users/@me"
        response = requests.get(
            endpoint, headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json()

    def get_guild(self, guild_id):
        endpoint = f"{self.base_url}/guilds/{guild_id}"
        response = requests.get(
            endpoint, headers={"Authorization": f"Bot {self.bot_access_token}"}
        )
        response.raise_for_status()
        return response.json()


discord_api = DiscordAPI()
