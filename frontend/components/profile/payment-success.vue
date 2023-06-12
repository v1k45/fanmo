<template>
<fm-dialog v-model="isVisible" require-explicit-close :show-close="showClose">
  <!-- creator's avatar start -->
  <div class="w-24 h-24 lg:w-32 lg:h-32 rounded-full relative overflow-hidden mx-auto mt-4">
    <img v-if="user.avatar" :src="user.avatar.medium" class="h-full w-full object-cover">
    <img v-else src="~/assets/logo-circle.png" class="h-full w-full object-cover">
  </div>
  <!-- creator's avatar end -->

  <!-- support {creator} & support-type success start -->
  <div class="my-4 font-semibold text-lg text-center">
    Payment Successful! <icon-check-circle-2 class="inline-block text-white bg-fm-success h-em w-em rounded-full mx-1 mb-1"></icon-check-circle-2>
  </div>
  <div class="text-center">
    <span v-if="supportType === 'membership'">
      You have successfully joined <span class="text-fm-primary">{{ tier.name }}</span>.
    </span>
    <span v-else-if="supportType === 'donation'">
      <template v-if="post">
        You have successfully unlocked <span class="font-semibold">{{ post.title }}</span> with a tip of <span class="font-semibold">{{ $currency(donationData.amount) }}</span>. A copy of this post has been sent to your email.
      </template>
      <template v-else>Your have successfully tipped <span class="font-semibold">{{ $currency(donationData.amount) }}</span>.</template>
    </span>
  </div>

  <div class="mt-4 text-center whitespace-pre-line">{{ successMessage }}</div>
  <!-- support {creator} & support-type success end -->

  <!-- buttons start -->
  <div v-if="$auth.loggedIn" class="mt-8 mb-6">
    <div v-if="supportType === 'membership' && !isPreview" class="flex space-x-3">
      <fm-button block @click="$emit('dashboard-click')">Go to Dashboard</fm-button>
      <fm-button block type="primary" @click="$emit('authenticated-next-click')">Ok</fm-button>
    </div>
    <div v-else-if="supportType === 'donation' && !isPreview" class="text-center">
      <fm-button class="w-36" @click="$emit('donation-close-click')">Ok</fm-button>
    </div>
  </div>
  <template v-else>
    <hr class="my-6">
    <fm-alert :show-icon="false">
      Your account has been created with the email provided during checkout. Please check your email for login instructions.
    </fm-alert>
    <div class="text-center mt-4 mb-6">
      <fm-button type="primary" @click="$emit('unauthenticated-next-click')">Activate account &rarr;</fm-button>
    </div>
  </template>
  <!-- buttons end -->

</fm-dialog>
</template>

<script>
import confetti from 'canvas-confetti';
import { delay } from '~/utils';

export default {
  props: {
    value: { type: Boolean, default: true },
    tier: { type: Object, default: null },
    user: { type: Object, required: true },
    post: { type: Object, required: false, default: null },
    successMessage: { type: String, default: null },
    donationData: { type: Object, default: null },
    showClose: { type: Boolean, default: false },
    supportType: { type: String, default: 'membership', validator: val => ['membership', 'donation'].includes(val) },
    isPreview: { type: Boolean, default: false }
  },
  data() {
    return {
      confetti: null
    };
  },
  computed: {
    isVisible: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('input', val);
      }
    }
  },
  watch: {
    isVisible(isVisible) {
      if (isVisible && this.confetti) this.fireConfetti();
    }
  },
  mounted() {
    this.confetti = confetti;
  },
  beforeDestroy() {
    const canvas = document.querySelector('canvas');
    if (canvas) canvas.remove();
  },
  methods: {
    async fireConfetti() {
      await delay(200); // wait for opening animation to finish
      this.confetti({
        particleCount: 300,
        spread: 150,
        origin: { y: 0.6 },
        disableForReducedMotion: true
      });
    }
  }
};
</script>

<style>

</style>
