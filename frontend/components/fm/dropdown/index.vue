<template>
<fm-popper
  v-slot="{ $reference, $popper, isVisible, hide }"
  v-bind="{
    placement,
    popperOptions: {
      strategy: 'fixed',
      modifiers: [
        {
          name: 'preventOverflow',
          options: {
            altAxis: true
          }
        }
      ]
    }
  }" class="fm-dropdown">
  <div v-bind="$reference" class="fm-dropdown__reference">
    <slot></slot>
  </div>
  <div v-show="isVisible" v-bind="$popper" class="fm-dropdown__content-wrapper" @click="hide">
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
  @apply absolute min-w-[175px] z-30;
  @apply p-2;
}
.fm-dropdown__content {
  @apply bg-white rounded-lg border min-w-max shadow-lg max-h-[80vh] overflow-auto;
}
</style>
