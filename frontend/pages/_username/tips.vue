<template>
<div class="container">
  <div class="row gx-0 lg:gx-4 max-w-6xl mx-auto justify-center">
    <div v-if="donations" class="col-12 order-2 lg:col-7 lg:order-1">
      <hr class="mt-6 mb-8 lg:hidden">
      <div class="text-xl font-bold mb-4">Recent tips</div>
      <fm-lazy v-for="(donation, idx) in donations" :key="donation.id"
        :class="{ 'mb-4 lg:mb-6': idx !== donations.length - 1 }" min-height="100">
        <profile-donation :donation="donation">
        </profile-donation>
      </fm-lazy>
      <div v-if="!donations.length" class="text-gray-500 text-center max-w-md mx-auto my-24">
        <template v-if="isSelfProfile">
          Your recent tips will show up here.
        </template>
        <template v-else>
          Become the first one to show your support for {{ user.display_name }}. Your contribution will show up here.
        </template>
      </div>
    </div>
    <div class="col-12 order-1 mb-6 sm:col-10 md:col-8 lg:col-5 lg:order-2 lg:mb-0">
      <donation-widget
        ref="donationWidget" :user="user" :loading="donationLoading"
        class="donation-card-sticky"
        @donate-click="$emit('donate', $event)">
      </donation-widget>
    </div>
  </div>
</div>

</template>

<script>
import { mapState } from 'vuex';

export default {
  props: {
    donationLoading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    ...mapState('profile', ['user', 'donations'])
  }
};
</script>
