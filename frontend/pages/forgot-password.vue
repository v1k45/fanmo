<template>
<div>
  <h1 class="font-title font-bold text-4xl text-center">Reset password</h1>


  <div class="mt-3 text-center">We'll send password reset instructions to your registered email address.</div>

  <div class="max-w-sm mx-auto">

    <fm-form :errors="errors" class="mt-8" @submit.prevent="resetPassword">

      <fm-input v-model="form.email" uid="email" type="email" placeholder="Email address" required autofocus></fm-input>

      <fm-button native-type="submit" type="primary" size="lg" class="mt-8" block>Reset password</fm-button>

    </fm-form>

    <div class="mt-6 text-center">
      <nuxt-link to="/login" class="text-fm-primary">&larr; Back to sign in</nuxt-link>.
    </div>
  </div>

</div>
</template>

<script>
const initialState = () => ({
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
    title: 'Forgot password'
  },
  methods: {
    async resetPassword() {
      try {
        await this.$axios.$post('/api/auth/password/reset/', this.form);
        const email = this.form.email;
        this.form.email = '';
        this.errors = {};
        this.$toast.success('Password reset instructions were sent to your email.');
        this.$router.push({ name: 'set-password', query: { email } });
      } catch (err) {
        this.errors = err.response.data;
      }
    }
  }
};
</script>
