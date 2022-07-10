<template>
<div class="text-center">Redirecting you to Facebook...</div>
</template>

<script>
export default {
  auth: false,
  layout: 'empty',
  async mounted() {
    await this.$auth.loginWith('facebook');
  }
};
</script>
