<template>
<main class="min-h-screen flex bg-gray-50">
  <div class="flex flex-grow justify-center items-center sm:p-4 md:p-8">
    <div class="max-w-md flex-grow card sm:bg-white sm:shadow-lg border">
      <div class="card-body">
        <h1 class="font-extrabold text-3xl">Sign up for fanmo</h1>
        <div class="font-medium mt-3">
          Already have an account?
          <nuxt-link to="/login" class="text-base font-medium text-primary ml-2">Sign in</nuxt-link>
        </div>

        <form class="mt-6" @submit.prevent="register">
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
          <button class="btn btn-primary btn-block mt-6 normal-case">Sign up</button>
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
      signupForm: {
        username: '',
        email: '',
        password1: '',
        password2: ''
      },
      signupErrors: {}
    };
  },
  head: {
    title: 'Sign up'
  },
  methods: {
    async register() {
      try {
        const response = await this.$axios.$post('/api/auth/register/', this.signupForm);
        this.$auth.setUser(response);
      } catch (err) {
        this.signupErrors = err.response.data;
      }
    }
  }
};
</script>
