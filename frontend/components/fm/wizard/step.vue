<template>
<div class="fm-wizard__step" :class="{ 'fm-wizard__step--finished': finished, 'fm-wizard__step--current': current }">
  <div class="fm-wizard__step-content">
    <div class="fm-wizard__step-icon">
      {{ id }}
    </div>
    <div v-if="$slots.default" class="fm-wizard__step-text">
      <slot></slot>
    </div>
  </div>
</div>
</template>

<script>
export default {
  props: {
    id: { type: [String, Number], default: '' },
    current: { type: Boolean, default: false },
    finished: { type: Boolean, default: false }
  }
};
</script>

<style lang="scss">
.fm-wizard__step {
  @apply flex-shrink-0 flex-1 text-center overflow-visible relative;

  &:not(:last-child):before {
    content: '';
    @apply absolute w-full h-1 bg-gray-300 top-4 -right-1/2;
  }
}
.fm-wizard__step-content {
  @apply relative inline-block text-center;
}
.fm-wizard__step-icon {
  @apply h-8 w-8 flex items-center justify-center font-bold rounded-full bg-gray-300 text-white mx-auto;
  @apply sm:h-9 sm:w-9 sm:text-xl;
}
.fm-wizard__step-text {
  @apply text-sm sm:text-base rounded-full mt-2 px-3;
}
.fm-wizard__step--finished {
  &:not(:last-child):before, .fm-wizard__step-icon {
    @apply bg-fm-success;
  }
}
.fm-wizard__step--current {
  .fm-wizard__step-icon {
    @apply bg-white border-fm-success border-4 text-fm-success;
  }
  .fm-wizard__step-text {
    @apply font-bold text-gray-900;
  }
}
</style>
