<template>
<profile :user="user"></profile>
</template>

<script>
import profile from './profile.vue';
export default {
  components: { profile },
  layout: 'default-no-container',
  async asyncData({ params, $axios }) {
    const user = await $axios.$get(`/api/users/${params.slug}/`);
    return { user };
  }
};
</script>
