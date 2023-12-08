<template>
<div class="container">
  <div class="max-w-6xl mx-auto">
    <div class="row justify-center gy-4 px-4">
      <div v-for="tier in user.tiers" :key="tier.id" class="col-12 md:col-6 lg:col-4">
        <profile-tier-card
          class="max-w-sm mx-auto h-full"
          v-bind="{ tier, loading: loadingTierId === tier.id }"
          @subscribe-click="$emit('subscribe', tier)">
        </profile-tier-card>
      </div>
    </div>

    <!-- no tier action start -->
    <fm-card
      v-if="!user.tiers.length"
      class="mx-auto max-w-xl overflow-hidden mt-6" body-class="text-center !pt-16 !pb-20">
      <icon-crown class="h-16 w-16 stroke-1 animatecss animatecss-tada"></icon-crown>
      <div class="mt-2">
        Make a steady monthly income while offering exclusive content and experience based on membership tiers to your fans.
      </div>
      <nuxt-link :to="{ name: 'members-tiers', params: { add: '1' } }">
        <fm-button type="primary" class="mt-4">Create your first tier &rarr;</fm-button>
      </nuxt-link>
    </fm-card>
    <!-- no tier action end -->

  </div>
</div>
</template>

<script>
import { mapState } from 'vuex';
export default {
  props: {
    loadingTierId: {
      type: Number,
      default: null
    }
  },
  computed: {
    ...mapState('profile', ['user'])
  }
};
</script>
