<template>
<button class="fm-dropdown__item" v-on="$listeners">
  <slot></slot>
</button>
</template>

<script>
export default {

};
</script>

<style lang="scss">
.fm-dropdown__item {
  @apply block w-full text-left p-3 cursor-pointer;
  &:hover {
    @apply bg-fm-primary-500 text-white;
  }
}
</style>
