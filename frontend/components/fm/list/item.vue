<template>
<li class="fm-list__item" :class="{ 'fm-list__item--actionable': actionable }">
  <slot></slot>
</li>
</template>

<script>
export default {
  props: {
    actionable: { type: Boolean, default: false }
  }
};
</script>
<style lang="scss">
.fm-list__item {
  @apply flex items-center border-l border-r border-b bg-white px-4 py-3;
}

.fm-list__item--actionable,
.fm-list--actionable > .fm-list__item {
  @apply cursor-pointer hover:bg-gray-200;
}
</style>
