<template>
<div class="text-center">Redirecting you to Facebook...</div>
</template>

<script>
export default {
  auth: false,
  layout: 'empty',
  head: {
    title: 'Redirecting to Facebook'
  },
  async created() {
    await this.$auth.loginWith('facebook');
  }
};
</script>
