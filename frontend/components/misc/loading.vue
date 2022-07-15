<template>
<div class="fixed z-30 top-0 left-0 h-full w-full flex flex-col justify-center items-center bg-white bg-opacity-80">
  <div class="animate-pulse">
    <logo circle class="h-16 w-16"></logo>
  </div>
  <div v-if="text" class="mt-3 text-lg text-black">{{ text }}</div>
</div>
</template>

<script>
export default {
  props: {
    text: { type: String, default: '' }
  }
};
</script>
