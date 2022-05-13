<template>
<div
  class="border bg-white border-gray-300 rounded-xl overflow-hidden relative"
  :class="{
    'min-h-[350px]': !hasGoodEnoughContent,
    'border-4 border-fm-success-600': tier.is_recommended
  }">

  <!-- cover start -->
  <figure v-if="tier.cover" class="w-full h-36 relative" :class="{ 'mt-4': tier.cover_background_style === 'contain' }">
    <img
      :src="tier.cover.full"
      class="absolute h-full w-full" alt="Tier image"
      :class="{ 'object-contain': tier.cover_background_style === 'contain', 'object-cover': tier.cover_background_style === 'cover' }">
  </figure>
  <!-- cover end -->

  <!-- private badge start -->
  <div class="absolute right-0 top-0 flex">
    <div
      v-if="tier.is_public === false"
      class="px-6 rounded-bl-lg py-1 text-sm bg-fm-error border-2 border-white border-r-0 border-t-0 text-white text-center right-0 top-0">
      Private
    </div>
    <div
      v-if="tier.is_recommended"
      class="px-6 rounded-bl-lg py-1 text-sm bg-fm-success-600 border-2 border-white border-r-0 border-t-0 text-white text-center right-0 top-0">
      Recommended
    </div>
  </div>
  <!-- private badge end -->

  <!-- everything else start -->
  <div class="py-4 px-6" :class="{ 'mt-4': !tier.cover }">
    <div class="text-center text-xl text-black font-bold truncate" :title="tier.name">{{ tier.name }}</div>

    <div class="text-center mt-2">
      <span class="text-3xl font-bold text-black">{{ $currency(tier.amount) }}</span>
      <span v-if="hasGoodEnoughContent" class="ml-0 text-sm">/ month</span>
      <div v-else class="mt-1 ml-0">per month</div>
    </div>

    <div v-if="editMode" class="mt-4 text-center">
      <fm-button class="w-48" @click="$emit('edit', tier)">Edit</fm-button>
    </div>
    <div v-else class="mt-4 text-center">
      <fm-button v-if="isAlreadySubscribed" type="success" class="w-48 pointer-events-none">
        <icon-check class="inline-block h-em w-em"></icon-check> Joined
      </fm-button>
      <fm-button v-else-if="isScheduledAfterCurrent" type="warning" class="w-48 pointer-events-none">
        <icon-clock class="inline-block h-em w-em"></icon-clock> Scheduled
      </fm-button>
      <fm-button v-else-if="isExpired" type="info" class="w-48" :loading="loading" @click="$emit('subscribe-click')">Rejoin</fm-button>
      <fm-button v-else type="primary" class="w-48" :loading="loading" @click="$emit('subscribe-click')">Join</fm-button>
    </div>

    <fm-read-more-height :max-height="tier.cover ? 100 : 200" class="mt-4">
      <div>{{ tier.description }}</div>

      <div class="mt-4">
        <ul class="space-y-2">
          <li v-for="(benefit, idx) in tier.benefits" :key="idx" class="flex">
            <icon-check-circle class="flex-shrink-0 mt-1 h-4 w-4 text-fm-success-600 stroke-[3] inline-block mr-2"></icon-check-circle>
            {{ benefit }}
          </li>
        </ul>
      </div>
    </fm-read-more-height>
  </div>
  <!-- everything else end -->

</div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import { CheckCircle as IconCheckCircle, Check as IconCheck } from 'lucide-vue';
export default {
  components: {
    IconCheckCircle,
    IconCheck
  },
  props: {
    tier: { type: Object, required: true },
    loading: { type: Boolean, default: false },
    editMode: { type: Boolean, default: false }
  },
  computed: {
    ...mapState('profile', ['user', 'existingMemberships']),
    ...mapGetters('profile', ['currentUserHasActiveAndScheduledSubscription']),
    hasGoodEnoughContent() {
      return this.tier.cover && this.tier.benefits.length;
    },
    isAlreadySubscribed() {
      if (!this.tier || !this.existingMemberships || !this.existingMemberships.length) return false;
      return (this.tier.id === this.existingMemberships[0].tier.id) && this.existingMemberships[0].is_active;
    },
    isExpired() {
      if (!this.tier || !this.existingMemberships || !this.existingMemberships.length) return false;
      return (this.tier.id === this.existingMemberships[0].tier.id) && !this.existingMemberships[0].is_active;
    },
    isScheduledAfterCurrent() {
      return (
        this.currentUserHasActiveAndScheduledSubscription &&
        this.existingMemberships[0].scheduled_subscription.tier.id === this.tier.id
      );
    }
  }
};
</script>

<style>

</style>
