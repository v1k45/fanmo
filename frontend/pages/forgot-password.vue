<template>
<div>
  <h1 class="font-title font-bold text-4xl text-center">Reset password</h1>


  <div class="mt-3 text-center">We'll send password reset instructions to your registered email address.</div>

  <div class="max-w-sm mx-auto">

    <fm-form :errors="errors" class="mt-8" @submit.prevent="resetPassword">

      <fm-input v-model="form.email" uid="email" type="email" placeholder="Email address" required autofocus></fm-input>

      <fm-button native-type="submit" type="primary" size="lg" class="mt-8" :loading="loading" block>Reset password</fm-button>

    </fm-form>

    <div class="mt-6 text-center">
      <nuxt-link to="/login" class="text-fm-primary">&larr; Back to sign in</nuxt-link>.
    </div>
  </div>

</div>
</template>

<script>
import { base64 } from '~/utils';

const initialState = () => ({
  loading: false,
  form: {
    email: ''
  },
  errors: {}
});
export default {
  layout: 'auth',
  auth: 'guest',
  data() {
    return initialState();
  },
  head: {
    title: 'Reset password'
  },
  methods: {
    async resetPassword() {
      this.loading = true;
      try {
        await this.$axios.$post('/api/auth/password/reset/', this.form);
        const email = this.form.email;
        this.form.email = '';
        this.errors = {};
        this.$toast.success('Password reset instructions were sent to your email.');
        this.loading = false;
        this.$router.push({ name: 'set-password-token', params: { token: base64.encode(email) } });
      } catch (err) {
        this.loading = false;
        this.errors = err.response.data;
      }
    }
  }
};
</script>
