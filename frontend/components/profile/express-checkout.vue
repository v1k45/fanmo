<template>
<fm-dialog v-model="isVisible" require-explicit-close custom-width dialog-class="max-w-lg">

  <!-- creator's avatar start -->
  <div class="w-24 h-24 lg:w-32 lg:h-32 rounded-full relative overflow-hidden mx-auto mt-4">
    <img v-if="user.avatar" :src="user.avatar.medium" class="h-full w-full object-cover">
    <img v-else src="~/assets/logo-circle.png" class="h-full w-full object-cover">
  </div>
  <!-- creator's avatar end -->

  <!-- support {creator} & support-type start -->
  <div class="mt-4 text-center text-black font-bold text-lg">Support {{ user.name || user.username }}</div>

  <div class="text-center text-gray-500 text-sm">
    <div v-if="supportType === 'membership'">
      Join <strong>{{ tier.name }}</strong> for
      <strong>{{ $currency(tier.amount) }}</strong> per month.
    </div>
    <div v-else-if="supportType === 'donation'">
      Send a one-time payment of <strong>{{ $currency(donationData.amount) }}</strong>.
    </div>
  </div>
  <!-- support {creator} & support-type end -->

  <!-- sign in options and email form start -->
  <div v-if="step === 'auth'" class="mt-6">
    <fm-form v-if="!$auth.loggedIn" :errors="errors" @submit.prevent="handleSubmit">
      <fm-input
        v-model="email" uid="email" label="Email address" type="email"
        placeholder="example@gmail.com" required :disabled="loading"></fm-input>

      <div class="mt-6">
        <div class="font-bold text-black uppercase text-sm text-center">or continue with</div>

        <div class="flex space-x-4">
          <fm-button size="lg" class="mt-4 flex items-center justify-center" block :disabled="loading" @click="handleSocialLogin('google')">
            <img src="~/assets/marketing/google.svg" class="h-6 inline-block mr-2" alt="Google G logo"> Google
          </fm-button>
          <fm-button size="lg" class="mt-4 flex items-center justify-center" block :disabled="loading" @click="handleSocialLogin('facebook')">
            <img src="~/assets/marketing/facebook.svg" class="h-6 inline-block mr-2" alt="Facebook F logo"> Facebook
          </fm-button>
        </div>
      </div>

      <fm-button native-type="submit" type="primary" class="mt-4" block :loading="loading">
        <div class="py-1 text-base">Proceed to payment</div>
      </fm-button>
    </fm-form>

    <div v-else class="text-center pt-16 pb-20 mx-auto">
      <icon-loader-2 class="h-16 w-16 stroke-1 animate-spin"></icon-loader-2>
      <div class="mt-2">
        Loading payment form...
      </div>
    </div>

    <!-- disclaimer start -->
    <div v-if="!$auth.loggedIn" class="mt-3 mb-8 text-xs text-center leading-relaxed text-gray-500">
      By continuing, you agree to the <a href="/terms" target="_blank">Terms &amp; conditions</a>
      and the <a href="/privacy" target="_blank">Privacy policy</a>.
    </div>
    <!-- disclaimer end -->
  </div>
  <!-- sign in options and email form end -->

  <!-- payment selection start -->
  <div v-if="step === 'payment'" class="mt-4 sm:mx-4">
    <fm-form :errors="errors" @submit.prevent="handlePaymentMethodSelection">

      <div class="mb-6 text-sm uppercase font-bold text-center animatecss">Select payment method</div>

      <fm-input v-model="paymentMethod" type="radio" native-value="upi" description="BHIM UPI, GPay, PhonePe, Paytm, etc.">
        <div>
          <img src="~/assets/marketing/upi.svg" class="h-6 inline-block" alt="UPI logo"> UPI
        </div>

        <div v-show="paymentMethod === 'upi'" class="animatecss animatecss-fadeIn">
          <div class="mt-4 text-xs">
            <fm-alert>
              <p class="font-bold">UPI AutoPay request will be sent to your app.</p>
              You can approve the request by selecting "AutoPay" or "Mandates" menu in your UPI app.
            </fm-alert>
          </div>
          <div class="my-2 text-xs">
            <a href="#" @click.prevent="showUPIHelp = !showUPIHelp">
              Where can I find the AutoPay menu? <icon-chevron-down v-if="!showUPIHelp" class="h-em w-em"></icon-chevron-down><icon-chevron-up v-else class="h-em w-em"></icon-chevron-up>
            </a>
            <div v-show="showUPIHelp" class="mt-2 text-gray-500">
              If there is a delay in the AutoPay notification, you can directly approve the request by following these steps:
              <ul class="mt-2 text-gray-500 list-disc list-inside">
                <li><strong>BHIM UPI</strong> &mdash; click on the <strong>Mandates</strong> menu on the home screen.</li>
                <li><strong>PhonePe</strong> &mdash; click on the <strong>Profile Icon</strong> on the top-left, go to <strong>Autopay Settings</strong>.</li>
                <li><strong>Google Pay</strong> &mdash; click on the <strong>Profile Icon</strong> on the top-right, go to <strong>Autopay</strong>.</li>
                <li><strong>Paytm</strong> &mdash; click on the <strong>Profile Icon</strong> on the top-left, click <strong>UPI &amp; Payment Settings</strong>, go to <strong>UPI Automatic Payments</strong>.</li>
              </ul>
            </div>
          </div>
        </div>

      </fm-input>

      <fm-input v-model="paymentMethod" type="radio" native-value="card" description="MasterCard and VISA cards">
        <div>
          <icon-credit-card class="h-6 w-6 stroke-2"></icon-credit-card> Card
        </div>

        <div v-show="paymentMethod === 'card'" class="animatecss animatecss-fadeIn">
          <div class="mt-4 text-xs">
            <fm-alert>
              <p class="font-bold">Cards issued by some banks may not work.</p>
              Due to recent RBI rules, subscription payments from some banks are temporarily stopped. If your card doesn't work, please try UPI or E-mandate during payment.
            </fm-alert>
            <p class="mt-2">Need help? email us on help@fanmo.in</p>
          </div>
        </div>
      </fm-input>

      <div class="text-center sm:mx-6 sm:mt-4">
        <fm-button native-type="submit" type="primary" class="mt-4" block :loading="loading">
          <div class="py-1 text-base">Confirm payment</div>
        </fm-button>
      </div>
    </fm-form>
    <div class="my-3 text-xs text-center leading-relaxed text-gray-500">
      Need help? email us on help@fanmo.in
    </div>
  </div>
  <!-- payment selection end -->

</fm-dialog>
</template>

<script>
import get from 'lodash/get';
import { mapActions } from 'vuex';
export default {
  props: {
    value: { type: Boolean, default: true },
    user: { type: Object, required: true },
    tier: { type: Object, default: null },
    donationData: { type: Object, default: null },
    supportType: { type: String, default: null, validator: val => ['membership', 'donation'].includes(val) }
  },
  data() {
    return {
      step: 'auth',
      email: '',
      paymentMethod: '',
      showUPIHelp: false,
      loading: false,
      errors: {},
      membership: {}
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
    async isVisible(isVisible) {
      if (isVisible) {
        if (this.$auth.loggedIn) {
          await this.handleSubmit();
        }
        return;
      }
      this.email = '';
      this.loading = false;
      this.errors = {};
      this.paymentMethod = '';
      this.step = 'auth';
      this.membership = {};
    }
  },
  methods: {
    ...mapActions('profile', ['createOrGetMembership', 'createDonation']),
    ...mapActions(['refreshUser']),
    async handleSubmit() {
      this.loading = true;
      if (this.supportType === 'membership') {
        const { success, data } = await this.createOrGetMembership({
          creator_username: this.user.username,
          tier_id: this.tier.id,
          email: this.email,
          period: this.$route.query.period
        });
        if (!success) {
          this.errors = data;
          this.loading = false;
          if (get(data, 'creator_username[0]')) this.$toast.error(data.creator_username[0].message);
          return;
        }
        this.membership = data;
        this.step = 'payment';
      } else {
        const { success, data } = await this.createDonation({
          ...this.donationData,
          email: this.email
        });
        if (!success) {
          this.errors = data;
          this.loading = false;
          if (get(data, 'creator_username[0]')) this.$toast.error(data.creator_username[0].message);
          return;
        }
        this.$emit('submit', data); // donation
      }
      this.loading = false;
      this.errors = {};
    },
    handlePaymentMethodSelection() {
      if (!this.paymentMethod) {
        this.$toast.error('Please select payment method.');
        return;
      }
      this.membership.scheduled_subscription.payment.payload.prefill.method = this.paymentMethod;
      this.$emit('submit', this.membership);
    },
    handleSocialLogin(provider) {
      const vm = this;
      window.onmessage = async ({ data }) => {
        if (data !== 'refresh_login' || vm.loading) return;
        window.onmessage = null;
        vm.loading = true;
        await vm.refreshUser();
        await vm.$nextTick();
        if (vm.$auth.loggedIn) {
          await vm.handleSubmit();
        } else {
          // TODO: track this as a sentry error to make sure it does not reappear.
          vm.$toast.error('Failed to login, please try again.');
          vm.loading = false;
        }
      };
      window.open(`/auth/callback/${provider}/`);
    }
  }
};
</script>

<style>

</style>
