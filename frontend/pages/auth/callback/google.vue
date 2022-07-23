<template>
<div class="text-center">
  Redirecting you to Google...
</div>
</template>

<script>
export default {
  auth: false,
  layout: 'empty',
  head: {
    title: 'Redirecting to Google'
  },
  async mounted() {
    await this.$auth.loginWith('google');
  }
};
</script>
