<template>
<fm-popper v-slot="{ $reference, $popper, isVisible }" v-bind="{ placement }" class="fm-dropdown">
  <div v-bind="$reference" class="fm-dropdown__reference">
    <slot></slot>
  </div>
  <div v-show="isVisible" v-bind="$popper" class="fm-dropdown__content-wrapper">
    <div class="fm-dropdown__content">
      <slot name="items"></slot>
    </div>
  </div>
</fm-popper>
</template>

<script>
export default {
  props: {
    placement: { type: String, default: 'bottom-start' }
  }
};
</script>

<style>
.fm-dropdown {
  @apply relative overflow-visible;
}
.fm-dropdown__reference {
  @apply inline-block;
}
.fm-dropdown__content-wrapper {
  @apply absolute min-w-[175px];
  @apply p-2;
}
.fm-dropdown__content {
  @apply bg-white rounded-lg overflow-hidden border min-w-max;
}
</style>
