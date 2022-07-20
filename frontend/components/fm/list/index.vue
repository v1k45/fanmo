<template>
<ul class="fm-list" :class="{ 'fm-list--actionable': actionable }">
  <slot></slot>
</ul>
</template>

<script>
export default {
  props: {
    actionable: { type: Boolean, default: false }
  }
};
</script>

<style lang="scss">
.fm-list {
  @apply border-t;
}
</style>
