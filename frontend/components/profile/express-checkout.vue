<template>
<fm-dialog v-model="isVisible" :close-on-backdrop-click="false" custom-width dialog-class="max-w-lg">

  <!-- creator's avatar start -->
  <div class="w-24 h-24 lg:w-32 lg:h-32 rounded-full relative overflow-hidden mx-auto mt-4">
    <img v-if="user.avatar" :src="user.avatar.medium" class="h-full w-full object-cover">
    <img v-else src="~/assets/avatar-placeholder.png" class="h-full w-full object-cover">
  </div>
  <!-- creator's avatar end -->

  <!-- support {creator} & support-type start -->
  <div class="mt-4 text-center text-black font-bold text-2xl">Support {{ user.name || user.username }}</div>

  <div v-if="supportType === 'membership'" class="text-center mt-1">
    by joining <strong class="text-black">{{ tier.name }}</strong> for
    <strong class="text-black">{{ $currency(tier.amount) }}</strong> per month.
  </div>
  <div v-else-if="supportType === 'donation'" class="text-center mt-1">
    with a one time payment of <strong class="text-black text-xl">{{ $currency(donationData.amount) }}</strong>
  </div>
  <!-- support {creator} & support-type end -->

  <!-- sign in options and email form start -->
  <div class="mt-8">
    <fm-form :errors="errors" @submit.prevent="handleSubmit">

      <fm-input
        v-model="email" uid="email" label="Email address" type="email"
        placeholder="example@gmail.com" required :disabled="loading"></fm-input>


      <div class="mt-6">
        <div class="font-bold text-black uppercase text-sm text-center">or continue with</div>

        <!-- TODO: figure out how this is supposed to work -->
        <div class="flex space-x-4">
          <fm-button size="lg" class="mt-4 flex items-center justify-center" block @click="handleGoogleLogin">
            <img src="~/assets/marketing/google.svg" class="h-6 inline-block mr-2" alt="Google G logo"> Google
          </fm-button>
          <fm-button size="lg" class="mt-4 flex items-center justify-center" block disabled>
            <img src="~/assets/marketing/facebook.svg" class="h-6 inline-block mr-2" alt="Facebook F logo"> Facebook
          </fm-button>
        </div>
      </div>

      <fm-button native-type="submit" type="primary" class="mt-4" block :loading="loading">
        <div class="py-1 text-base">Proceed with payment</div>
      </fm-button>
    </fm-form>
  </div>
  <!-- sign in options and email form end -->

  <!-- disclaimer start -->
  <div class="mt-3 mb-8 text-sm leading-relaxed text-gray-500">
    By continuing, you agree to the <nuxt-link to="/terms">Terms &amp; conditions</nuxt-link>
    and the <nuxt-link to="/privacy">Privacy policy</nuxt-link>.
  </div>
  <!-- disclaimer end -->

</fm-dialog>
</template>

<script>
import { mapActions, mapState } from 'vuex';
export default {
  props: {
    value: { type: Boolean, default: true },
    tier: { type: Object, default: null },
    donationData: { type: Object, default: null },
    supportType: { type: String, default: null, validator: val => ['membership', 'donation'].includes(val) }
  },
  data() {
    return {
      email: '',
      loading: false,
      errors: {}
    };
  },
  computed: {
    ...mapState('profile', ['user']),

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
      if (isVisible) return;
      this.email = '';
      this.loading = false;
      this.errors = {};
    }
  },
  methods: {
    ...mapActions('profile', ['createOrGetMembership', 'createDonation']),
    async handleSubmit() {
      this.loading = true;
      if (this.supportType === 'membership') {
        const { success, data } = await this.createOrGetMembership({
          creator_username: this.user.username,
          tier_id: this.tier.id,
          email: this.email
        });
        if (!success) {
          this.errors = data;
          this.loading = false;
          return;
        }
        this.$emit('submit', data); // membership
      } else {
        const { success, data } = await this.createDonation({
          ...this.donationData,
          email: this.email
        });
        if (!success) {
          this.errors = data;
          this.loading = false;
          return;
        }
        this.$emit('submit', data); // donation
      }
      this.loading = false;
      this.errors = {};
    },
    handleGoogleLogin() {
      // todo: show a loading indicator in checkout form while login is being completed?
      // todo: remove listener?
      window.onmessage = async () => {
        // todo: filter messages?
        // handle case where login fails or is abandoned for some reason?
        await this.$auth.fetchUser();
        await this.handleSubmit();
      };
      window.open('/auth/callback/google/');
    }
  }
};
</script>

<style>

</style>
