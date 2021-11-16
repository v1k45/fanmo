<template>
<div class="absolute top-0 left-0 h-full w-full flex flex-col justify-center items-center bg-white bg-opacity-80">
  <icon-loader class="w-12 h-12 animate-spin text-success stroke-current"></icon-loader>
  <div v-if="text" class="mt-3">{{ text }}</div>
</div>
</template>

<script>
export default {
  props: {
    text: { type: String, default: '' }
  }
};
</script>
