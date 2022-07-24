<template>
<div>
  <h1 class="font-title font-bold text-4xl text-center">Set password</h1>

  <div class="max-w-sm mx-auto mb-10">
    <fm-form :errors="errors" class="mt-8" @submit.prevent="setPassword">

      <fm-input v-model="form.email" uid="email" label="Email" type="email" block required readonly></fm-input>

      <fm-input v-model="form.code" uid="code" label="OTP" type="otp" block required autofocus></fm-input>

      <div class="text-right my-4 text-sm">
        Don't have one?
        <fm-button type="link" class="mr-auto" @click="sendOTP">Get a password reset code</fm-button>
      </div>

      <fm-input v-model="form.new_password" uid="new_password" label="New password" type="password" required></fm-input>

      <fm-button native-type="submit" type="primary" size="lg" class="mt-6" :loading="loading" block>Set password</fm-button>
    </fm-form>
  </div>
</div>
</template>

<script>
import { base64 } from '~/utils';

const initialFormState = () => ({
  loading: false,
  form: {
    email: '',
    code: '',
    new_password: ''
  },
  errors: {}
});
export default {
  layout: 'auth',
  auth: 'guest',
  data() {
    return {
      ...initialFormState()
    };
  },
  head: {
    title: 'Set password'
  },
  mounted() {
    try {
      const email = base64.decode(this.$route.params.token || '');
      if (!/\S+@\S+\.\S+/.test(email)) throw new Error('Invalid email');
      this.form.email = email;

      if (this.$route.query.s === '1') this.sendOTP();
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('(Handled)', err);
      this.$router.replace({ name: 'forgot-password' });
    }
  },
  methods: {
    async sendOTP() {
      this.loading = true;
      try {
        await this.$axios.$post('/api/auth/password/reset/', { email: this.form.email });
        this.$toast.success('Password reset code was sent to your email.');
        this.errors = {};
      } catch (err) {
        this.errors = err.response.data;
      }
      this.loading = false;
    },
    async setPassword() {
      this.loading = true;
      try {
        await this.$axios.$post('/api/auth/password/reset/confirm/', this.form);
        this.$toast.success('Your password was set successfully.');
        await this.$auth.loginWith('cookie', { data: { email: this.form.email, password: this.form.new_password } });
        Object.assign(this, initialFormState());
        this.loading = false;
      } catch (err) {
        this.loading = false;
        this.errors = err.response.data;
      }
    }
  }
};
</script>
