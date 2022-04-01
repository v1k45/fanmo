<template>
<div class="fixed z-30 top-0 left-0 h-full w-full flex flex-col justify-center items-center bg-white bg-opacity-80">
  <div class="text-5xl select-none animate-spin origin-center">⌛</div>
  <div v-if="text" class="mt-3 text-black">{{ text }}</div>
</div>
</template>

<script>
export default {
  props: {
    text: { type: String, default: '' }
  }
};
</script>
