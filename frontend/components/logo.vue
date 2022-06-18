<template>
<naked-circle-logo v-if="circle" :class="{ 'text-fm-primary': !uncolored }"></naked-circle-logo>
<img v-else src="~/assets/logo.svg" alt="Fanmo logo with text">
</template>
<script>
import NakedCircleLogo from '~/assets/logo-naked-no-underline.svg?inline';

export default {
  components: {
    NakedCircleLogo
  },
  props: {
    circle: { type: Boolean, default: false },
    uncolored: { type: Boolean, default: false }
  }
};
</script>
