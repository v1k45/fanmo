<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <!-- header start -->
  <misc-page-header class="container sm:pl-0" :page="pages.settings"></misc-page-header>
  <!-- header end -->

  <!-- container start -->
  <div class="mt-5 pb-16 rounded-xl border bg-white">


    <nuxt-child></nuxt-child>

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
    };
  },
  head: {
    title: 'Settings'
  },
  computed: {
    ...mapState('ui', ['pages'])
  },
  created() {
    this.setCurrentPage('settings');
  },
  methods: {
    ...mapMutations('ui', ['setCurrentPage'])
  }
};
</script>
