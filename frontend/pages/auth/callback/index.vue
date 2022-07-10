<template>
<fm-card
  v-if="waiting"
  class="mx-auto max-w-xl overflow-hidden" body-class="text-center !pt-16 !pb-20">
  <icon-loader-2 class="h-16 w-16 stroke-1 animate-spin"></icon-loader-2>
  <div class="mt-2">
    Please wait while we process your login request...
  </div>
</fm-card>
<fm-card
  v-else
  class="mx-auto max-w-xl overflow-hidden" body-class="text-center !pt-16 !pb-20">
  <icon-server-crash class="h-16 w-16 stroke-1 animatecss animatecss-spin"></icon-server-crash>
  <div class="mt-2 font-medium">
    Looks like was an error while logging you in.
  </div>
  <div class="mt-2">
    Please make to grant email permission on your Google or Facebook Authorization Screen.
  </div>
  <nuxt-link :to="{ name: 'login' }">
    <fm-button type="primary" class="mt-4">Try again</fm-button>
  </nuxt-link>
</fm-card>
</template>

<script>
export default {
  auth: false,
  data() {
    return {
      waiting: true
    };
  },
  mounted() {
    // consider the authorization request as failed if the user is not redirected in 5 seconds.
    setTimeout(() => {
      this.waiting = false;
    }, 5000);
  }
};
</script>
