<template>
<profile :username="$route.params.username"></profile>
</template>

<script>
import profile from './profile.vue';
export default {
  components: { profile },
  auth: false,
  layout: 'default-no-container'
};
</script>
