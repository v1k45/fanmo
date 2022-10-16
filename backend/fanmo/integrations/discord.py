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
    bot_auth_headers = {"Authorization": f"Bot {bot_access_token}"}

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

    def refresh_token(self, refresh_token):
        endpoint = self.base_url + "/oauth2/token"
        response = requests.post(
            endpoint,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
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
        response = requests.get(endpoint, headers=self.bot_auth_headers)
        response.raise_for_status()
        return response.json()

    def add_guild_member(self, guild_id, user_id, access_token):
        endpoint = f"{self.base_url}/guilds/{guild_id}/members/{user_id}"
        payload = {"access_token": access_token}
        response = requests.put(endpoint, json=payload, headers=self.bot_auth_headers)
        response.raise_for_status()

    def remove_guild_member(self, guild_id, user_id):
        endpoint = f"{self.base_url}/guilds/{guild_id}/members/{user_id}"
        response = requests.delete(endpoint, headers=self.bot_auth_headers)
        response.raise_for_status()

    def add_guild_member_role(self, guild_id, user_id, role_id):
        endpoint = (
            f"{self.base_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}"
        )
        response = requests.put(endpoint, headers=self.bot_auth_headers)
        response.raise_for_status()

    def remove_guild_member_role(self, guild_id, user_id, role_id):
        endpoint = (
            f"{self.base_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}"
        )
        response = requests.delete(endpoint, headers=self.bot_auth_headers)
        response.raise_for_status()


discord_api = DiscordAPI()
