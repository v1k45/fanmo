<template>
<main class="min-h-screen flex bg-gray-50">
  <div class="flex flex-grow justify-center items-center sm:p-4 md:p-8">
    <div class="max-w-md flex-grow card sm:bg-white sm:shadow-lg border">
      <div class="card-body">
        <h1 class="font-extrabold text-3xl">
          Reset Password
        </h1>
        <div class="font-medium mt-3">
          Remember Password?
          <nuxt-link class="text-base font-medium text-primary ml-2" to="/login">Login</nuxt-link>
        </div>
        <div v-if="sent">
          Check your email for link to reset password.
        </div>
        <form v-else class="mt-6" @submit.prevent="resetPassword">
          <error-alert :errors="errors"></error-alert>
          <div class="form-control">
            <label class="label label-text">Email address</label>
            <input v-model="form.email" type="email" class="input input-bordered" :class="{ 'input-error': errors.email }" required>
            <label v-for="(error, index) in errors.email" :key="index" class="label">
              <span class="label-text-alt">{{ error.message }}</span>
            </label>
          </div>
          <button class="btn btn-primary btn-block mt-4 normal-case">Reset Password</button>
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
      sent: false,
      form: {
        email: ''
      },
      errors: {}
    };
  },
  head: {
    title: 'Forgot password'
  },
  methods: {
    async resetPassword() {
      try {
        await this.$axios.$post('/api/auth/password/reset/', this.form);
        this.sent = true;
      } catch (err) {
        this.errors = err.response.data;
      }
    }
  }
};
</script>
