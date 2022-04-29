<template>
<div v-if="!$auth.loggedIn">
  Logging you in...
</div>
<div v-else>
  You are already logged in
</div>
</template>

<script>
export default {
  auth: false,
  layout: 'empty',
  async mounted() {
    if (!this.$auth.loggedIn && this.$route.params.callback !== 'callback') {
      await this.$auth.loginWith(this.$route.params.callback);
    } else {
      // write better code?
      window.opener.postMessage('refresh_login', {});
      window.close();
    }
  }
};
</script>
