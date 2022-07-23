<template>
<div>
  <h1 class="font-title font-bold text-4xl text-center">Sign in</h1>
  <div class="mt-10 text-center">
    Don't have an account? <nuxt-link to="/register" class="text-fm-primary">Register here</nuxt-link>.
  </div>

  <div class="max-w-sm mx-auto mt-8">
    <fm-form :errors="loginErrors" @submit.prevent="userLogin">

      <fm-input v-model="loginForm.email" uid="email" label="Email" type="email" required autofocus></fm-input>

      <fm-input v-model="loginForm.password" uid="password" label="Password" type="password" required></fm-input>

      <div class="text-right mt-4">
        <nuxt-link to="/forgot-password" class="text-fm-primary">Forgot password?</nuxt-link>
      </div>

      <fm-button native-type="submit" type="primary" size="lg" class="mt-6" :loading="loading" block>Sign in</fm-button>
    </fm-form>

    <div class="mt-6">
      <div class="font-bold text-black uppercase text-sm text-center">or continue in with</div>

      <div class="flex space-x-4">
        <fm-button size="lg" class="mt-6 flex items-center justify-center" block @click="$auth.loginWith('google')">
          <img src="~/assets/marketing/google.svg" class="h-6 inline-block mr-2" alt="Google G logo"> Google
        </fm-button>
        <fm-button size="lg" class="mt-6 flex items-center justify-center" block @click="$auth.loginWith('facebook')">
          <img src="~/assets/marketing/facebook.svg" class="h-6 inline-block mr-2" alt="Facebook F logo"> Facebook
        </fm-button>
      </div>
    </div>

  </div>
</div>
</template>

<script>
export default {
  layout: 'auth',
  auth: 'guest',
  data() {
    return {
      loading: false,
      loginForm: {
        email: '',
        password: ''
      },
      loginErrors: {}
    };
  },
  head: {
    title: 'Sign in'
  },
  methods: {
    async userLogin() {
      this.loading = true;
      try {
        await this.$auth.loginWith('cookie', { data: this.loginForm });
        this.loginErrors = {};
      } catch (err) {
        this.loginErrors = err.response.data;
      }
      this.loading = false;
    }
  }
};
</script>
