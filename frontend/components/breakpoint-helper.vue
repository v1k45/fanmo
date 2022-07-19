<template>
<div v-if="isDev" class="inline-block text-xl font-bold">
  <div class="sm:hidden">XS</div>
  <div class="hidden sm:inline-block md:hidden">SM</div>
  <div class="hidden md:inline-block lg:hidden">MD</div>
  <div class="hidden lg:inline-block xl:hidden">LG</div>
  <div class="hidden xl:inline-block 2xl:hidden">XL</div>
  <div class="hidden 2xl:inline-block">2XL</div>
</div>
</template>

<script>
export default {
  data() {
    return {
      isDev: process.env.NODE_ENV !== 'production'
    };
  }
};
</script>
