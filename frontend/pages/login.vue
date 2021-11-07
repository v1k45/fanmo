<template>
<main class="min-h-screen flex bg-gray-50">
  <div class="flex flex-grow justify-center items-center sm:p-4 md:p-8">
    <div class="max-w-md flex-grow card sm:bg-white sm:shadow-lg border">
      <div class="card-body">
        <h1 class="font-extrabold text-3xl">
          {{ modeText.title }} {{ signin ? 'to' : 'for' }}
          <span class="text-success"><span class="text-primary">Patr</span>kaar</span>
        </h1>
        <div class="font-medium mt-3">
          {{ modeText.alternateActionDescription }}
          <button class="text-base font-medium text-primary ml-2" @click="signin = !signin;">{{ modeText.alternateAction }}</button>
        </div>

        <form v-if="signin" class="mt-6" @submit.prevent>
          <div class="form-control">
            <label class="label label-text">Username or email address</label>
            <input type="text" class="input input-bordered">
          </div>
          <div class="form-control mt-3">
            <label class="label label-text">Password</label>
            <input type="password" class="input input-bordered">
            <div class="text-right mt-2">
              <button class="text-sm text-primary">Forgot password?</button>
            </div>
          </div>
          <button class="btn btn-primary btn-block mt-4 normal-case">{{ modeText.title }}</button>
        </form>
        <form v-else class="mt-6" @submit.prevent>
          <div class="form-control">
            <label class="label label-text">Username</label>
            <input type="text" class="input input-bordered">
          </div>
          <div class="form-control mt-3">
            <label class="label label-text">Email address</label>
            <input type="text" class="input input-bordered">
          </div>
          <div class="form-control mt-3">
            <label class="label label-text">Password</label>
            <input type="password" class="input input-bordered">
          </div>
          <div class="form-control mt-3">
            <label class="label label-text">Confirm password</label>
            <input type="password" class="input input-bordered">
          </div>
          <button class="btn btn-primary btn-block mt-6 normal-case">{{ modeText.title }}</button>
        </form>
      </div>
    </div>
  </div>
</main>
</template>

<script>
export default {
  layout: 'empty',
  data() {
    return {
      signin: true
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
  }
};
</script>
