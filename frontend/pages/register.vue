<template>
<div>
  <h1 class="font-title font-bold text-4xl text-center">Sign up for <logo class="h-7 inline-block ml-2"></logo></h1>

  <div class="mt-10 text-center">
    Already have an account? <nuxt-link to="/login" class="text-fm-primary">Sign in here</nuxt-link>.
  </div>

  <div class="max-w-sm mx-auto mt-8">
    <fm-form :errors="signupErrors" @submit.prevent="register">
      <fm-input v-model="signupForm.name" uid="name" placeholder="Display name" autofocus required></fm-input>

      <fm-input v-model="signupForm.email" uid="email" type="email" placeholder="Email address" required></fm-input>

      <fm-input v-model="signupForm.password" uid="password" type="password" placeholder="Password" required></fm-input>

      <div class="text-sm mt-6 leading-relaxed">
        By creating an account, you agree to the <nuxt-link to="/terms">Terms &amp; conditions</nuxt-link>
        and the <nuxt-link to="/privacy">Privacy policy</nuxt-link>.
      </div>

      <fm-button native-type="submit" type="primary" size="lg" class="mt-6" block>Create account</fm-button>
    </fm-form>

    <div class="mt-6">
      <div class="font-bold text-black uppercase text-sm text-center">or continue with</div>

      <div class="flex space-x-4">
        <fm-button size="lg" class="mt-6 flex items-center justify-center" block @click="socialLogin">
          <img src="~/assets/marketing/google.svg" class="h-6 inline-block mr-2" alt="Google G logo"> Google
        </fm-button>
        <fm-button size="lg" class="mt-6 flex items-center justify-center" block>
          <img src="~/assets/marketing/facebook.svg" class="h-6 inline-block mr-2" alt="Facebook F logo"> Facebook
        </fm-button>
      </div>
    </div>

  </div>
</div>
</template>

<script>
import faker from 'faker';
// TODO: remove faker
const USE_FAKE = false;

export default {
  layout: 'auth',
  auth: 'guest',
  data() {
    const fake = USE_FAKE
      ? {
          name: faker.name.firstName(),
          email: faker.internet.email(),
          password: faker.internet.password()
        }
      : null;
    return {
      signupForm: fake || {
        name: '',
        email: '',
        password: ''
      },
      signupErrors: {}
    };
  },
  head: {
    title: 'Sign up for Fanmo'
  },
  methods: {
    async register() {
      try {
        await this.$axios.$post('/api/auth/register/', this.signupForm);
        await this.$auth.loginWith('cookie', { data: this.signupForm });
        this.signupErrors = {};
        this.$toast.success('Your account was created successfully!');
      } catch (err) {
        this.signupErrors = err.response.data;
      }
    },
    async socialLogin() {
      // TODO: test if we need to switch back to cookie
      await this.$auth.loginWith('google');
    }
  }
};
</script>
