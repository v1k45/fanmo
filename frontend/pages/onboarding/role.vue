<template>
<div>
  <h1 class="font-title font-bold text-3xl text-center">Select your role</h1>

  <div class="max-w-sm mx-auto">

    <div class="mt-3 text-center text-gray-500 text-sm">
      Select the option that best describes what you primarily intend to use the platform as.
    </div>

    <fm-form :errors="errors" class="mt-8" @submit.prevent="setAccountType">

      <fm-input v-model="form.is_creator" uid="is_creator" :native-value="true" name="type" type="radio" required>
        <div class="font-bold">I'm a creator</div>
        <div class="text-xs mt-1">You will still be able to support your favorite creators.</div>
      </fm-input>
      <fm-input v-model="form.is_creator" uid="is_creator" :native-value="false" name="type" type="radio" required>
        <div class="font-bold">I'm here to support creators</div>
        <div class="text-xs mt-1">Don't worry, you can change your account type at any time.</div>
      </fm-input>

      <fm-button native-type="submit" type="primary" size="lg" class="mb-6 mt-8" block>Next</fm-button>

    </fm-form>
  </div>

</div>
</template>

<script>
const initialState = () => ({
  form: {
    is_creator: null
  },
  errors: {}
});
export default {
  layout: 'auth-empty',
  data() {
    return initialState();
  },
  head: {
    title: 'Select your role'
  },
  computed: {
    isConfirmed() {
      return this.$auth.user.onboarding.checklist.email_verification;
    }
  },
  created() {
    this.form.is_creator = this.$auth.user.is_creator;
  },
  methods: {
    async setAccountType() {
      try {
        const user = await this.$axios.$patch('/api/me/', this.form);
        this.$auth.setUser(user);
        Object.assign(this, initialState());
        if (this.$auth.user.is_creator || !this.isConfirmed) this.$router.push({ name: 'onboarding-verify' });
        else this.$router.push('/auth/');
      } catch (err) {
        this.errors = err.response.data;
      }
    }
  }
};
</script>
