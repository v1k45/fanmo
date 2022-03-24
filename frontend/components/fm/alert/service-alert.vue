<template>
<transition
  enter-active-class="animatecss-bounceInDown"
  leave-active-class="animatecss-bounceOutUp"
  @after-leave="$emit('closed')">
  <fm-alert v-if="isVisible" class="animatecss animatecss-faster" v-bind="{ type, title, message }">
    <template v-if="html">
      <div v-html="message"></div>
    </template>
    <template v-else>{{ message }}</template>
  </fm-alert>
</transition>
</template>

<script>
import { delay } from '~/utils';

export default {
  props: {
    type: { type: String, default: null },
    title: { type: String, default: '' },
    message: { type: String, default: '' },
    timeout: { type: Number, default: 0 },
    html: { type: Boolean, default: false }
  },
  data() {
    return {
      isVisible: false
    };
  },
  async mounted() {
    this.isVisible = true;
    if (!this.timeout) return;
    await delay(this.timeout);
    this.isVisible = false;
  }
};
</script>

<style lang="scss">
.fm-alert__container {
  @apply fixed left-1/2 transform -translate-x-1/2 top-3 z-30 flex flex-col items-center;
  @apply w-[95vw] max-w-max;
  > .fm-alert {
    @apply w-full max-w-lg;
  }
  > .fm-alert ~ .fm-alert {
    @apply mt-1;
  }
}
.fm-alert-enter-active {
  @apply animatecss-bounceInDown;
}
.fm-alert-leave-active {
  @apply animatecss-bounceOutUp;
}
</style>
