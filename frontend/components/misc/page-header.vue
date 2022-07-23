<template>
<div>
  <div class="text-2xl text-black font-bold">{{ (page.supporterTitle && !$auth.user.is_creator) ? page.supporterTitle : page.title }}</div>
  <div class="mt-1 text-gray-600">{{ page.description }}</div>
</div>
</template>

<script>
export default {
  props: {
    page: { type: Object, required: true }
  }
};
</script>
