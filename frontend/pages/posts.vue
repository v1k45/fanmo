<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <!-- header start -->
  <misc-page-header class="container sm:pl-0" :page="pages.posts"></misc-page-header>
  <!-- header end -->

  <!-- container start -->
  <div class="mt-5 pb-16 rounded-xl border bg-white">

    <div class="flex mt-2 mb-8 border-b-2 justify-center lg:justify-start">
      <nuxt-link
        v-for="item in nav" :key="item.name" :to="item.url" replace
        class="px-8 py-3 unstyled block relative font-medium text-black"
        exact-active-class="!text-fm-primary font-bold">
        {{ item.label }}

        <div v-if="$route.name === item.name" class="absolute left-0 bottom-[-2px] w-full h-[2px] bg-fm-primary"></div>
      </nuxt-link>
    </div>

    <div class="md:px-8 container">
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
        { name: 'posts', label: 'Posts', url: '/posts/' },
        { name: 'posts-sections', label: 'Sections', url: '/posts/sections/' }
      ]
    };
  },
  computed: {
    ...mapState('ui', ['pages'])
  },
  created() {
    this.setCurrentPage('posts');
  },
  methods: {
    ...mapMutations('ui', ['setCurrentPage'])
  }
};
</script>
