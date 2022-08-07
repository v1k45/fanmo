<template>
<fm-dialog v-model="isVisible" :close-on-backdrop-click="false" :show-close="showClose">
  <!-- creator's avatar start -->
  <div class="w-24 h-24 lg:w-32 lg:h-32 rounded-full relative overflow-hidden mx-auto mt-4">
    <img v-if="user.avatar" :src="user.avatar.medium" class="h-full w-full object-cover">
    <img v-else src="~/assets/logo-circle.png" class="h-full w-full object-cover">
  </div>
  <!-- creator's avatar end -->

  <!-- support {creator} & support-type success start -->
  <div class="mt-4 text-black font-bold text-xl text-center">
    <span class="mr-2">
      <icon-check-circle class="inline-block text-fm-success h-7 w-7 stroke-[3]"></icon-check-circle>
    </span>
    <span v-if="supportType === 'membership'">
      You have successfully joined <span class="text-fm-primary">{{ tier.name }}</span>.
    </span>
    <span v-else-if="supportType === 'donation'">
      Your one-time payment of <span class="text-fm-primary">{{ $currency(donationData.amount) }}</span> was successful.
    </span>
  </div>

  <div class="mt-4 text-center whitespace-pre-line">{{ successMessage }}</div>
  <!-- support {creator} & support-type success end -->

  <!-- buttons start -->
  <div v-if="$auth.loggedIn" class="mt-8 mb-6">
    <div v-if="supportType === 'membership'" class="flex space-x-3">
      <fm-button block @click="$emit('dashboard-click')">Dashboard</fm-button>
      <fm-button block type="primary" @click="$emit('authenticated-next-click')">Done</fm-button>
    </div>
    <div v-else-if="supportType === 'donation'" class="text-center">
      <fm-button class="w-36" @click="$emit('donation-close-click')">Done</fm-button>
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
import { CheckCircle as IconCheckCircle } from 'lucide-vue';
import { delay } from '~/utils';

export default {
  components: {
    IconCheckCircle
  },
  props: {
    value: { type: Boolean, default: true },
    tier: { type: Object, default: null },
    user: { type: Object, required: true },
    successMessage: { type: String, default: null },
    donationData: { type: Object, default: null },
    showClose: { type: Boolean, default: false },
    supportType: { type: String, default: 'membership', validator: val => ['membership', 'donation'].includes(val) }
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
