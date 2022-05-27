<template>
<div v-if="!$auth.loggedIn">
  Redirecting to Google...
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
    if (!this.$auth.loggedIn) {
      await this.$auth.loginWith('google');
    } else {
      // write better code?
      window.opener.postMessage('refresh_login', {});
      window.close();
    }
  }
};
</script>
