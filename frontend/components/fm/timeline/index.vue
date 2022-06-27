<template>
<div class="fm-timeline">
  <slot></slot>
</div>
</template>

<script>
export default {

};
</script>
<style lang="scss">
.fm-timeline {
  @apply grid;
  grid-template-columns: auto 1fr;
  grid-auto-rows: minmax(40px, auto);
}
</style>
