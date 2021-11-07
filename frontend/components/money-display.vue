<template>
<span class="inline-flex items-center">
  <icon-indian-rupee :size="size"></icon-indian-rupee><slot></slot>
</span>
</template>
<script>
export default {
  props: {
    size: { type: Number, default: 16 }
  }
};
</script>
