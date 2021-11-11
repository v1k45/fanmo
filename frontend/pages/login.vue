<template>
<main class="min-h-screen flex bg-gray-50">
  <div class="flex flex-grow justify-center items-center sm:p-4 md:p-8">
    <div class="max-w-md flex-grow card sm:bg-white sm:shadow-lg border">
      <div class="card-body">
        <h1 class="font-extrabold text-3xl">
          {{ modeText.title }} {{ signin ? 'to' : 'for' }} fanmo
        </h1>
        <div class="font-medium mt-3">
          {{ modeText.alternateActionDescription }}
          <button class="text-base font-medium text-primary ml-2" @click="signin = !signin;">{{ modeText.alternateAction }}</button>
        </div>

        <form v-if="signin" class="mt-6" @submit.prevent="userLogin">
          <error-alert :errors="loginErrors"></error-alert>
          <div class="form-control">
            <label class="label label-text">Email address</label>
            <input v-model="loginForm.email" type="email" class="input input-bordered" :class="{ 'input-error': loginErrors.email }" required>
            <label v-for="(error, index) in loginErrors.email" :key="index" class="label">
              <span class="label-text-alt">{{ error.message }}</span>
            </label>
          </div>
          <div class="form-control mt-3">
            <label class="label label-text">Password</label>
            <input v-model="loginForm.password" type="password" class="input input-bordered" required>
            <div class="text-right mt-2">
              <nuxt-link to="/forgot-password" class="text-sm text-primary">Forgot password?</nuxt-link>
            </div>
          </div>
          <button class="btn btn-primary btn-block mt-4 normal-case">{{ modeText.title }}</button>
        </form>
        <form v-else class="mt-6" @submit.prevent="register">
          <error-alert :errors="signupErrors"></error-alert>
          <div class="form-control">
            <label class="label label-text">Username</label>
            <input v-model="signupForm.username" type="text" class="input input-bordered" :class="{ 'input-error': signupErrors.username }" required>
            <label v-for="(error, index) in signupErrors.username" :key="index" class="label">
              <span class="label-text-alt">{{ error.message }}</span>
            </label>
          </div>
          <div class="form-control mt-3">
            <label class="label label-text">Email address</label>
            <input v-model="signupForm.email" type="text" class="input input-bordered" :class="{ 'input-error': signupErrors.email }" required>
            <label v-for="(error, index) in signupErrors.email" :key="index" class="label">
              <span class="label-text-alt">{{ error.message }}</span>
            </label>
          </div>
          <div class="form-control mt-3">
            <label class="label label-text">Password</label>
            <input v-model="signupForm.password1" type="password" class="input input-bordered" :class="{ 'input-error': signupErrors.password1 }" required>
            <label v-for="(error, index) in signupErrors.password1" :key="index" class="label">
              <span class="label-text-alt">{{ error.message }}</span>
            </label>
          </div>
          <div class="form-control mt-3">
            <label class="label label-text">Confirm password</label>
            <input v-model="signupForm.password2" type="password" class="input input-bordered" :class="{ 'input-error': signupErrors.password2 }" required>
            <label v-for="(error, index) in signupErrors.password2" :key="index" class="label">
              <span class="label-text-alt">{{ error.message }}</span>
            </label>
          </div>
          <button class="btn btn-primary btn-block mt-6 normal-case">{{ modeText.title }}</button>
        </form>
      </div>
    </div>
  </div>
</main>
</template>

<script>
import errorAlert from '../components/ui/error-alert.vue';
export default {
  components: { errorAlert },
  layout: 'empty',
  auth: 'guest',
  data() {
    return {
      signin: true,
      loginForm: {
        email: '',
        password: ''
      },
      loginErrors: {},
      signupForm: {
        username: '',
        email: '',
        password1: '',
        password2: ''
      },
      signupErrors: {}
    };
  },
  computed: {
    modeText() {
      return this.signin
        ? {
            title: 'Sign in',
            alternateAction: 'Sign up',
            alternateActionDescription: 'Don\'t have an account?'
          }
        : {
            title: 'Sign up',
            alternateAction: 'Sign in',
            alternateActionDescription: 'Already have an account?'
          };
    }
  },
  methods: {
    async userLogin() {
      try {
        const response = await this.$auth.loginWith('cookie', { data: this.loginForm });
        console.log(response);
      } catch (err) {
        console.log(err);
        this.loginErrors = err.response.data;
      }
    },
    async register() {
      try {
        const response = await this.$axios.$post('/api/auth/register/', this.signupForm);
        console.log(response);
        this.$auth.setUser(response);
      } catch (err) {
        console.log(err);
        this.signupErrors = err.response.data;
      }
    }
  }
};
</script>
