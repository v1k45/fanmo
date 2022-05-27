<template>
<div v-if="!$auth.loggedIn">
  Redirecting...
</div>
<div v-else>
  You are already logged in
</div>
</template>

<script>
export default {
  auth: false,
  layout: 'empty',
  mounted() {
    // write better code?
    window.opener.postMessage('refresh_login', {});
    window.close();
  }
};
</script>
