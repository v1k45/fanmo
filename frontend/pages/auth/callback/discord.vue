<template>
<fm-card
  v-if="waiting"
  class="mx-auto max-w-xl overflow-hidden" body-class="text-center !pt-16 !pb-20">
  <icon-loader-2 class="h-16 w-16 stroke-1 animate-spin"></icon-loader-2>
  <div class="mt-2">
    Please wait while we process your connect request...
  </div>
</fm-card>
<fm-card
  v-else
  class="mx-auto max-w-xl overflow-hidden" body-class="text-center !pt-16 !pb-20">
  <icon-server-crash class="h-16 w-16 stroke-1 animatecss animatecss-spin"></icon-server-crash>
  <div class="mt-2 font-medium">
    Looks like there was an error while connecting your discord.
  </div>
  <div class="mt-2">
    {{ errorMessage || 'Please try again.' }}
  </div>
  <nuxt-link :to="{ name: 'settings', query: { tab: 'discord' } }">
    <fm-button type="primary" class="mt-4">Try again</fm-button>
  </nuxt-link>
</fm-card>
</template>

<script>
import get from 'lodash/get';
import { handleGenericError } from '~/utils';

export default {
  auth: true,
  data() {
    return {
      waiting: true,
      errorMessage: ''
    };
  },
  head: {
    title: 'Connecting your discord...'
  },
  async mounted() {
    this.waiting = true;
    if (this.$route.query.error) {
      this.errorMessage = 'You seem to have cancelled the connection request.';
      this.waiting = false;
      return;
    }

    const provider = this.$route.query.guild_id ? 'discord_server' : 'discord_user';
    try {
      await this.$axios.$post(`/api/integrations/${provider}/`, {
        code: this.$route.query.code,
        redirect_uri: `${window.location.origin}/auth/callback/discord/`
      });
      this.$router.push({ name: 'settings', query: { tab: 'discord' } });
    } catch (e) {
      handleGenericError(e);
      this.errorMessage = get(e.response.data, 'non_field_errors[0].message');
      this.waiting = false;
    }
  }
};
</script>
