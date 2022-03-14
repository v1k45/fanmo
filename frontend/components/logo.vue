<template>
<img v-if="circle" src="~/assets/logo-naked.png" alt="Fanmo circle logo">
<img v-else src="~/assets/logo.png" alt="Fanmo logo with text">
</template>
<script>
export default {
  props: {
    circle: { type: Boolean, default: false }
  }
};
</script>
