<template>
<nuxt-link class="flex items-center space-x-3" v-if="user" :to="`/${user.username}`">
  <div class="avatar">
    <div class="w-12 h-12 mask mask-circle">
      <img :src="user.avatar.small" alt="Profile picture">
    </div>
  </div>
  <div class="font-bold">{{ user.display_name }}</div>
</nuxt-link>
<div class="flex items-center space-x-3" v-else>
  <div class="avatar placeholder">
    <div class="w-12 h-12 rounded-full bg-neutral-focus text-neutral-content">
      <span class="text-3xl">?</span>
    </div>
  </div>
  <div class="font-bold">Anonymous</div>
</div>

</template>

<script>
export default {
  props: {
    user: {
      type: Object
    }
  }
};
</script>
