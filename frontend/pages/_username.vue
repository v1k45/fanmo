<template>
<profile :username="$route.params.username"></profile>
</template>

<script>
import profile from './profile.vue';
// TODO: do data fetching here and set title based on that
export default {
  components: { profile },
  auth: false,
  layout: 'default-no-container',
  head() {
    return {
      title: this.$route.params.username
    };
  }
};
</script>
