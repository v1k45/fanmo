<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <!-- header start -->
  <misc-page-header class="container sm:pl-0" :page="pages.receivedDonations"></misc-page-header>
  <!-- header end -->

  <!-- container start -->
  <div class="mt-5 pb-16 rounded-xl border bg-white">

    <div class="flex mt-2 mb-8 border-b-2 justify-center lg:justify-start">
      <nuxt-link
        v-for="item in nav" :key="item.id" :to="item.url" replace
        class="px-8 py-3 unstyled block relative font-medium text-black"
        exact-active-class="!text-fm-primary font-bold">
        {{ item.label }}

        <div v-if="$route.path === item.url" class="absolute left-0 bottom-[-2px] w-full h-[2px] bg-fm-primary"></div>
      </nuxt-link>
    </div>

    <div class="lg:px-8 container">
      <nuxt-child></nuxt-child>
    </div>

  </div>
  <!-- container end -->

</div>
</template>

<script>
import { mapMutations, mapState } from 'vuex';

export default {
  layout: 'with-sidebar',
  data() {
    return {
      nav: [
        { id: 'index', label: 'Donations', url: '/received-donations/' },
        { id: 'donation-settings', label: 'Settings', url: '/received-donations/settings/' }
      ]
    };
  },
  computed: {
    ...mapState('ui', ['pages'])
  },
  created() {
    this.setCurrentPage('receivedDonations');
  },
  methods: {
    ...mapMutations('ui', ['setCurrentPage'])
  }
};
</script>
