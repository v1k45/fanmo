<template>
<div class="fm-wizard">
  <div class="fm-wizard__steps">
    <slot></slot>
  </div>
</div>
</template>

<script>
export default {
};
</script>

<style lang="scss">
.fm-wizard {
  @apply overflow-auto max-w-full pb-4;
}
.fm-wizard__steps {
  @apply flex justify-between overflow-visible;
}
</style>
