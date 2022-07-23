<template>
<div>
  <h1 class="font-title font-bold text-4xl text-center">Create an account</h1>

  <div class="mt-4 text-center">
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

      <fm-button native-type="submit" type="primary" size="lg" class="mt-6" block :loading="loading">Create account</fm-button>
    </fm-form>

    <div class="mt-6">
      <div class="font-bold text-black uppercase text-sm text-center">or continue with</div>

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
      signupForm: {
        name: '',
        email: '',
        password: ''
      },
      signupErrors: {}
    };
  },
  head: {
    title: 'Create an account'
  },
  methods: {
    async register() {
      this.loading = true;
      try {
        await this.$axios.$post('/api/auth/register/', this.signupForm);
        await this.$auth.loginWith('cookie', { data: this.signupForm });
        this.signupErrors = {};
        this.$toast.success('Your account was created successfully!');
      } catch (err) {
        this.signupErrors = err.response.data;
      }
      this.loading = false;
    }
  }
};
</script>
