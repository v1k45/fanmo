<template>
<div class="fixed z-30 top-0 left-0 h-full w-full flex flex-col justify-center items-center bg-white bg-opacity-80">
  <icon-loader-2 class="select-none animate-spin h-8 w-8"></icon-loader-2>
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
