<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <!-- header start -->
  <div class="container sm:pl-0">
    <div class="text-2xl text-black font-bold">Settings</div>
    <div class="mt-1 text-gray-600">Manage your account, notifications and security settings.</div>
  </div>
  <!-- header end -->

  <!-- container start -->
  <div class="mt-5 pb-16 rounded-xl border bg-white">


    <nuxt-child></nuxt-child>

  </div>
  <!-- container end -->

</div>
</template>

<script>
export default {
  layout: 'with-sidebar',
  data() {
    return {
    };
  },
  head: {
    title: 'Settings'
  }
};
</script>
