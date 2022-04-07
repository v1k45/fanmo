<template>
<fm-card>
  <div class="flex items-center">
    <fm-avatar
      :src="donation.fan_user.avatar && donation.fan_user.avatar.small"
      :name="donation.fan_user.name" :username="donation.fan_user.username"
      size="w-10 h-10 flex-shrink-0">
    </fm-avatar>
    <div class="ml-3 mr-auto min-w-0">
      <div class="text-lg md:text-xl font-medium truncate" :title="donation.fan_user.display_name">
        {{ donation.fan_user.display_name }}
      </div>
      <div class="flex">
        <div class="text-xs text-gray-500">{{ createdAt }}</div>
      </div>
    </div>
    <div class="ml-3 flex-shrink-0 self-start leading-none">
      <span class="font-medium text-lg md:text-xl text-black">{{ $currency(donation.amount) }}</span>
    </div>
    <div v-if="isSelfProfile && donation.message" class="ml-2 flex-shrink-0 self-start mt-0.5">
      <fm-dropdown placement="bottom-end">
        <button class="hover:text-fm-primary hover:scale-105 transform flex" title="Options">
          <span class="sr-only">Options</span>
          <icon-more-vertical class="h-6 w-6 text-gray-500"></icon-more-vertical>
        </button>
        <template #items>
          <fm-dropdown-item @click="toggleMessageVisibility(donation)">
            <template v-if="!donation.is_hidden">
              <icon-lock class="inline-block -mt-1 h-em w-em"></icon-lock> Make message private
            </template>
            <template v-else>
              <icon-unlock class="inline-block -mt-1 h-em w-em"></icon-unlock> Make message public
            </template>
          </fm-dropdown-item>
        </template>
      </fm-dropdown>
    </div>
  </div>

  <div class="ml-10 pl-3">
  </div>

  <fm-read-more-height v-if="donation.message" max-height="200" class="mt-4">
    <div
      v-if="isCurrentUserDonator && isSelfProfile && donation.is_hidden && donation.message"
      class="inline-flex items-start text-xs md:text-sm px-1 sm:px-2 rounded bg-fm-warning text-white mb-2">
      <icon-lock class="inline-block mt-0.5 mr-1 w-auto h-em"></icon-lock> Message is only visible to yourself.
    </div>
    <template v-else>
      <div
        v-if="isCurrentUserDonator && donation.is_hidden && donation.message"
        class="inline-flex items-start text-xs md:text-sm px-1 sm:px-2 rounded bg-fm-warning text-white mb-2">
        <icon-lock class="inline-block mt-0.5 mr-1 w-auto h-em"></icon-lock> Message is only visible to you and the creator.
      </div>
      <div
        v-if="isSelfProfile && donation.is_hidden && donation.message"
        class="inline-flex items-start text-xs md:text-sm px-1 sm:px-2 rounded bg-fm-warning text-white mb-2">
        <icon-lock class="inline-block mt-0.5 mr-1 w-auto h-em"></icon-lock> Message is only visible to you and the supporter.
      </div>
    </template>
    <div class="whitespace-pre-wrap overflow-auto">{{ donation.message }}</div>
  </fm-read-more-height>
</fm-card>
</template>

<script>
import dayjs from 'dayjs';
import { mapActions, mapGetters } from 'vuex';

export default {
  props: {
    donation: { type: Object, required: true }
  },
  data() {
    return {
      step: 1,
      subscriptionForm: {
      },
      subscriptionErrors: {}
    };
  },
  computed: {
    ...mapGetters('profile', ['isSelfProfile']),
    createdAt() {
      if (!this.donation) return '';
      return dayjs(this.donation.created_at).format('D MMM, YYYY hh:mma');
    },
    isCurrentUserDonator() {
      return this.$auth.loggedIn && this.$auth.user.username === this.donation.fan_user.username;
    }
  },
  methods: {
    ...mapActions('profile', ['updateDonation']),
    toggleMessageVisibility() {
      this.updateDonation({ id: this.donation.id, payload: { is_hidden: !this.donation.is_hidden } });
    }
  }
};
</script>
