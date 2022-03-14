<template>
<div>
  <button
    class="absolute left-4 top-4 text-black"
    title="Back to role selection" @click="$router.push({ name: 'onboarding-role' })">
    <icon-arrow-left></icon-arrow-left>
  </button>
  <h1 class="font-title font-bold text-3xl text-center">Confirm your email</h1>

  <div v-show="!isConfirmed" class="mt-3 text-center text-gray-500 text-sm">We've sent a verification code to {{ $auth.user.email }}.</div>

  <div class="max-w-sm mx-auto">

    <fm-form v-show="!isConfirmed" :errors="errors" class="mt-8" @submit.prevent="verifyEmail">

      <fm-input v-model="form.code" uid="code" label="Enter the received code" type="otp" block required autofocus></fm-input>

      <div class="text-right mt-4">
        <fm-button type="link" @click="resendOTP">Resend verification code</fm-button>
      </div>

      <fm-button native-type="submit" type="primary" size="lg" class="mt-6" block>Verify</fm-button>

      <fm-button
        v-if="!$auth.user.is_creator"
        native-type="button" type="link" size="lg" class="mt-4 mb-6" block
        @click="skipForNow">
        Skip for now
      </fm-button>

    </fm-form>

    <div v-if="isConfirmed" class="mt-4">
      <fm-alert type="success">Your email has already been confirmed!</fm-alert>
      <fm-button type="primary" size="lg" class="mt-6" block @click="navigateToNext">Next</fm-button>
    </div>
  </div>

</div>
</template>

<script>
import { ArrowLeft as IconArrowLeft } from 'lucide-vue';
import { skipOnboarding } from '~/utils';
const initialState = () => ({
  form: {
    code: ''
  },
  errors: {}
});
export default {
  components: {
    IconArrowLeft
  },
  layout: 'auth-empty',
  data() {
    return initialState();
  },
  head: {
    title: 'Verify your account'
  },
  computed: {
    isConfirmed() {
      return this.$auth.user.onboarding.checklist.email_verification;
    }
  },
  mounted() {
    this.resendOTP();
  },
  methods: {
    navigateToNext() {
      if (this.$auth.user.is_creator) {
        this.$router.replace({ name: 'onboarding-profile-info' });
      } else {
        this.$router.replace('/');
      }
    },
    async resendOTP() {
      try {
        await this.$axios.$post('/api/auth/email/verify/', this.form);
        Object.assign(this, initialState());
        this.$toast.info('A verification code was sent to your email.');
      } catch (err) {
        this.errors = err.response.data;
      }
    },
    // TODO: redirect to last visited page
    async verifyEmail() {
      try {
        await this.$axios.$post('/api/auth/email/verify/confirm/', this.form);
        await this.$auth.fetchUser();
        Object.assign(this, initialState());
        this.navigateToNext();
        this.$toast.success('Your account was verified successfully!');
      } catch (err) {
        this.errors = err.response.data;
      }
    },
    // TODO: redirect to last visited page
    skipForNow() {
      skipOnboarding.set(this.$auth.user.username);
      this.$router.push('/');
    }
  }
};
</script>
