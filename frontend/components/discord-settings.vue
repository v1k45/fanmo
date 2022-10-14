<template>
<div>
  <template v-if="$auth.user.is_creator">
    <div class="text-xl font-medium text-black flex items-center">Discord Server</div>
    <div class="text-gray-500 mt-2 text-sm mt-4 max-w-xl">
      Automatically manage invitations and role assignments of your members using Discord Integration.
    </div>
    <div class="text-gray-500 mt-2 text-sm mt-4 max-w-xl">
      Members who connect their discord account to Fanmo will be automatically granted permissions to access your Discord Server.
      Their Discord role will be updated when they upgrade, downgrade or cancel their membership.
    </div>
    <div v-if="integrations.discord_server" class="max-w-md mx-auto lg:mx-0 mt-4">
      <fm-alert type="success" class="mt-4 text-sm">
        Your discord server "{{ integrations.discord_server.name }}" is connected.
      </fm-alert>
      <div class="text-lg font-medium mt-4">Roles</div>
      <ul class="list-disc ml-4">
        <li v-for="role in integrations.discord_server.roles" :key="role.id">{{ role.name }}</li>
      </ul>
      <div class="my-4 p-4 border rounded">
        <fm-input :value="integrations.discord_server.kick_inactive_members" :disabled="isIntegrationLoading" type="checkbox" @input="updateDiscordServer">
          Kick inactive members from server
        </fm-input>
        <div class="text-gray-500 mt-2 text-xs">
          By default, only the associated role is removed. This is useful when you have a public Discord with private channels for members of specific roles.
        </div>
      </div>
      <div class="flex space-x-2 my-4">
        <fm-button :loading="isIntegrationLoading" @click="refreshDiscordRoles"><icon-refresh-cw class="h-em w-em"></icon-refresh-cw> Refresh roles</fm-button>
        <fm-button type="error" :loading="isIntegrationLoading" @click="removeDiscordServer"><icon-slash class="h-em w-em"></icon-slash> Remove Connection</fm-button>
      </div>
    </div>
    <a v-else :href="discordAuth.server">
      <fm-button type="primary" class="mt-4">Connect Discord Server</fm-button>
    </a>
    <hr class="my-8">
  </template>

  <div class="text-xl font-medium text-black flex items-center">Discord Account</div>
  <div class="text-gray-500 mt-2 text-sm mt-4 max-w-xl">
    Many creators offer Discord access as membership benefits.
    Connect your account to automatically get invited when you become a member.
  </div>
  <div v-if="integrations.discord_user" class="max-w-md mx-auto lg:mx-0 mt-6">
    <fm-alert type="success" class="mt-4 text-sm">
      Your discord user "{{ integrations.discord_user.name }}" is connected.
    </fm-alert>
    <fm-button class="mt-4" type="error" :loading="isIntegrationLoading" @click="removeDiscordUser"><icon-slash class="h-em w-em"></icon-slash> Remove Connection</fm-button>
  </div>
  <a v-else :href="discordAuth.user">
    <fm-button type="primary" class="mt-4">Connect Discord</fm-button>
  </a>
</div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { handleGenericError } from '~/utils';

export default {
  data() {
    return {
      isIntegrationLoading: false
    };
  },
  computed: {
    ...mapState('users', ['integrations']),
    discordAuth() {
      const authUrl = new URL('https://discord.com/api/oauth2/authorize');
      authUrl.searchParams.append('redirect_uri', `${window.location.origin}/auth/callback/discord/`);
      authUrl.searchParams.append('client_id', this.$config.discord);
      authUrl.searchParams.append('response_type', 'code');

      const serverUrl = new URL(authUrl.href);
      serverUrl.searchParams.append('permissions', 268435459);
      serverUrl.searchParams.append('scope', 'email identify bot');

      const userUrl = new URL(authUrl.href);
      userUrl.searchParams.append('scope', 'email identify guilds.join');
      return {
        server: serverUrl.href,
        user: userUrl.href
      };
    }
  },
  created() {
    this.loadIntegrations();
  },
  methods: {
    ...mapActions('users', ['loadIntegrations']),
    refreshDiscordRoles() {
      this.updateDiscordServer(this.integrations.discord_server.kick_inactive_members);
    },
    async updateDiscordServer(kick) {
      this.isIntegrationLoading = true;
      try {
        await this.$axios.$patch('/api/integrations/discord_server/', { refresh: true, kick_inactive_members: kick });
        await this.$toast.info('Discord server updated successfully.');
      } catch (err) {
        handleGenericError(err, true);
      }
      await this.loadIntegrations();
      this.isIntegrationLoading = false;
    },
    async removeDiscordServer() {
      try {
        await this.$confirm.error(
          [
            'Are you sure you want to remove connection?',
            'New members will stop getting invited to your discord server.'].join('<br>'),
          'Confirm',
          { html: true }
        );
      } catch (err) {
        return;
      }

      this.isIntegrationLoading = true;
      try {
        await this.$axios.$delete('/api/integrations/discord_server/');
        await this.$toast.info('Discord Server was removed.');
      } catch (err) {
        handleGenericError(err, true);
      }
      await this.loadIntegrations();
      this.isIntegrationLoading = false;
    },
    async removeDiscordUser() {
      try {
        await this.$confirm.error(
          [
            'Are you sure you want to remove connection?',
            'Any discord invitations made through Fanmo will be revoked.'].join('<br>'),
          'Confirm',
          { html: true }
        );
      } catch (err) {
        return;
      }

      this.isIntegrationLoading = true;
      try {
        await this.$axios.$delete('/api/integrations/discord_user/');
        await this.$toast.info('Your connection was removed.');
      } catch (err) {
        handleGenericError(err, true);
      }
      await this.loadIntegrations();
      this.isIntegrationLoading = false;
    }
  }
};
</script>
