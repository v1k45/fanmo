<template>
<div>
  <h1 class="font-title font-bold text-4xl text-center">Set new password</h1>

  <div class="max-w-sm mx-auto mb-10">
    <fm-alert v-if="done" type="success" class="mt-4">Your password was successfully updated.</fm-alert>

    <fm-form :errors="errors" class="mt-8" @submit.prevent="setPassword">


      <fm-input v-model="form.code" uid="code" label="OTP" type="otp" block required autofocus></fm-input>

      <div class="text-right mt-4 text-sm">
        Don't have one?
        <nuxt-link to="/forgot-password" class="mr-auto">Get a password reset code</nuxt-link>.
      </div>

      <fm-input v-show="false" v-model="form.email" uid="email" label="Email" type="email" required></fm-input>
      <fm-input v-model="form.new_password" uid="new_password" label="New password" type="password" required></fm-input>

      <fm-button native-type="submit" type="primary" size="lg" class="mt-6" block>Set password</fm-button>
    </fm-form>
  </div>
</div>
</template>

<script>
const initialFormState = () => ({
  done: false,
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
  created() {
    this.form.email = this.$route.query.email || '';
  },
  methods: {
    async setPassword() {
      try {
        await this.$axios.$post('/api/auth/password/reset/confirm/', this.form);
        Object.assign(this, initialFormState());
        this.done = true;
        setTimeout(() => {
          this.$router.push({ name: 'login' });
        }, 3000);
      } catch (err) {
        this.errors = err.response.data;
      }
    }
  }
};
</script>
