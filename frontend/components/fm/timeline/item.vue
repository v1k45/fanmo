<template>
<fragment>
  <div class="fm-timeline__item-icon">
    <div class="fm-timeline__item-tail" :class="tailClass"></div>
    <slot name="icon">
      <div class="relative border-4 bg-white border-fm-primary h-3 w-3 mt-[7px] rounded-full"></div>
    </slot>
  </div>
  <div class="fm-timeline__item-content">
    <span>
      <slot></slot>
    </span>
  </div>
</fragment>
</template>

<script>
import { Fragment } from 'vue-fragment';

export default {
  components: {
    Fragment
  },
  props: {
    tailClass: { type: [String, Array, Object], default: 'bg-fm-primary w-[2px]' } // for setting the bg and width yourself
  }
};
</script>
<style lang="scss">
.fm-timeline__item-icon {
  @apply flex justify-center items-baseline mr-2 relative;
  &:nth-last-child(2) > .fm-timeline__item-tail {
    @apply hidden;
  }
}
.fm-timeline__item-tail {
  @apply absolute top-[7px] h-full left-1/2 transform -translate-x-1/2;
}
.fm-timeline__item-content {
}
</style>
