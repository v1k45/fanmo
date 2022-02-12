<template>
<main class="min-h-screen flex bg-gray-50">
  <div class="flex flex-grow justify-center items-center sm:p-4 md:p-8">
    <div class="max-w-md flex-grow card sm:bg-white sm:shadow-lg border">
      <div class="card-body">
        <h1 class="font-extrabold text-3xl">
          Sign in to fanmo
        </h1>
        <div class="font-medium mt-3">
          Don't have an account?
          <nuxt-link to="/signup" class="text-base font-medium text-primary ml-2">Sign up</nuxt-link>
        </div>

        <button class="btn btn-primary btn-block my-4 normal-case" @click="socialLogin">Sign in with Google</button>
        <hr>

        <form class="mt-6" @submit.prevent="userLogin">
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
          <button class="btn btn-primary btn-block mt-4 normal-case">Sign in</button>
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
      loginErrors: {}
    };
  },
  head: {
    title: 'Sign in'
  },
  methods: {
    async userLogin() {
      try {
        await this.$auth.loginWith('cookie', { data: this.loginForm });
      } catch (err) {
        this.loginErrors = err.response.data;
      }
    },
    async socialLogin() {
      // todo: test if we need to switch back to cookie
      await this.$auth.loginWith('google');
    }
  }
};
</script>
