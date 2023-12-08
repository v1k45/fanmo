<template>
<button class="fm-dropdown__item" :class="{
  'fm-dropdown__item--error': type === 'error',
  'fm-dropdown__item--static': $props.static,
  'fm-dropdown__item--active': active
}" type="button" v-on="$listeners">
  <slot></slot>
</button>
</template>

<script>
export default {
  props: {
    static: { type: Boolean, default: false },
    type: { type: String, default: '', validator: val => !val || ['error'].includes(val) },
    active: { type: Boolean, default: false }
  }
};
</script>

<style lang="scss">
.fm-dropdown__item {
  @apply block w-full text-left p-3 cursor-pointer;
  &:hover {
    @apply bg-fm-primary-500 text-white;
  }
}
.fm-dropdown__item--error {
  @apply text-fm-error;
  &:hover {
    @apply bg-fm-error text-white;
  }
}
.fm-dropdown__item--static {
  @apply cursor-auto pointer-events-none;
}
.fm-dropdown__item--active {
  @apply bg-fm-primary-500 text-white;
}
</style>
