<template>
<main class="sm:py-16 bg-gray-50 min-h-screen">
  <logo class="h-8 mx-auto"></logo>
  <div class="max-w-lg mx-auto mt-10">
    <fm-wizard>
      <fm-wizard-step id="1" finished><span class="text-sm">Create account</span></fm-wizard-step>
      <fm-wizard-step id="2" current><span class="text-sm">Complete profile</span></fm-wizard-step>
      <fm-wizard-step id="3"><span class="text-sm">Add payment details</span></fm-wizard-step>
    </fm-wizard>
  </div>
  <fm-card class="max-w-lg mx-auto py-4 sm:px-4 mt-4 relative">
    <button
      class="absolute left-4 top-4 text-black"
      title="Back to role selection" @click="$router.push({ name: 'onboarding-role' })">
      <icon-arrow-left></icon-arrow-left>
    </button>
    <div class="max-w-sm mx-auto">

      <fm-form :errors="errors" @submit.prevent="setProfileInfo">

        <h1 class="font-title font-bold text-2xl text-center mb-4">A little about yourself!</h1>
        <fm-input
          v-model="form.name" uid="name" type="text"
          placeholder="Eg. The Arctic Fox Podcast" required autofocus>
          <template #label>
            Page name
            <span class="text-xs">(This will be displayed on your profile)</span>
          </template>
        </fm-input>
        <fm-input v-model="form.onboarding.full_name" uid="onboarding.full_name" type="text" required>
          <template #label>
            Full name
            <span class="text-xs">(Private. To be used for verification and payouts)</span>
          </template>
        </fm-input>

        <h1 class="font-title font-bold text-2xl text-center mt-8 mb-0">Where can we find you?</h1>

        <fm-input
          v-model="form.onboarding.introduction" uid="onboarding.introduction"
          placeholder="Add your social links, phone number, best way for us to reach out to you."
          rows="4" type="textarea" required>
        </fm-input>

        <fm-button native-type="submit" type="primary" size="lg" class="mt-8 mb-6" block>Next</fm-button>

      </fm-form>
    </div>

  </fm-card>
</main>
</template>

<script>
import get from 'lodash/get';

const initialState = (user) => {
  return {
    form: {
      name: get(user, 'name'),
      onboarding: {
        full_name: get(user, 'onboarding.full_name'),
        introduction: get(user, 'onboarding.introduction')
      }
    },
    errors: {}
  };
};
export default {
  layout: 'empty',
  data() {
    return initialState(this.$auth.user);
  },
  head: {
    title: 'Profile information'
  },
  methods: {
    async setProfileInfo() {
      try {
        const user = await this.$axios.$patch('/api/me/', this.form);
        this.$auth.setUser(user);
        this.errors = {};
        this.$toast.success('Your profile information was saved successfully!');
        this.$router.replace({ name: 'onboarding-payment-info' });
      } catch (err) {
        this.errors = err.response.data;
      }
    }
  }
};
</script>
