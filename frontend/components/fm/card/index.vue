<template>
<section class="fm-card">
  <header v-if="$slots.header" class="fm-card__header">
    <slot name="header"></slot>
  </header>
  <div class="fm-card__body" :class="bodyClass">
    <slot></slot>
  </div>
</section>
</template>

<script>
export default {
  props: {
    bodyClass: { type: [String, Array], default: '' }
  }
};
</script>

<style lang="scss">
.fm-card {
  @apply bg-white rounded-xl border;
}
.fm-card__header {
  @apply font-bold border-b px-6 py-3 text-xl;
}
.fm-card__body {
  @apply px-6 py-4;
}
</style>
