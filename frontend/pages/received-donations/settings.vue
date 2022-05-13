<template>
<div>
  <div class="max-w-lg">
    <fm-form :errors="errors" @submit.prevent="save">
      <fm-input
        v-model="form.donation_description" :disabled="loading"
        uid="preferences.donation_description" type="textarea" rows="4" label="Description"
        description="This will be shown in the donation widget. Tell your audience how their support will help you."
        :placeholder="`Show your appreciation for ${$auth.user.display_name} with a one time payment.`">
      </fm-input>

      <fm-input
        v-model="form.thank_you_message"
        uid="preferences.thank_you_message" :disabled="loading"
        type="textarea" rows="4" placeholder="Thank you for supporting me! 🎉">
        <template #label>
          <div class="flex items-end">
            <label class="mr-auto">Thank you message</label>
            <fm-button size="sm" @click="isPaymentSuccessPreviewVisible = true;">Preview</fm-button>
          </div>
          <div class="text-sm text-gray-500 mt-1">This will be shown to your supporters after they make a donation. A copy will also be sent to their email.</div>
        </template>
      </fm-input>

      <fm-button block type="primary" native-type="submit" class="mt-8" :loading="loading">Save</fm-button>
    </fm-form>
  </div>

  <!-- nested dialog start -->
  <profile-payment-success
    v-model="isPaymentSuccessPreviewVisible"
    support-type="donation"
    :user="$auth.user"
    :donation-data="donationData"
    :success-message="form.thank_you_message"
    @donation-close-click="isPaymentSuccessPreviewVisible = false;">
  </profile-payment-success>
  <!-- nested dialog end -->
</div>
</template>

<script>
import random from 'lodash/random';
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      random,
      loading: false,
      isPaymentSuccessPreviewVisible: false,
      form: {
        donation_description: '',
        thank_you_message: ''
      },
      errors: {}
    };
  },
  computed: {
    donationData() {
      return this.isPaymentSuccessPreviewVisible ? { amount: random(50, 2000) } : { amount: 0 };
    }
  },
  watch: {
    '$auth.user.preferences': {
      immediate: true,
      handler(preferences) {
        this.form = {
          donation_description: preferences.donation_description,
          thank_you_message: preferences.thank_you_message
        };
      }
    }
  },
  methods: {
    ...mapActions('users', ['updateSelfUser']),
    async save() {
      this.loading = true;
      const { success, data } = await this.updateSelfUser({ preferences: this.form });
      if (success) {
        this.$toast.success('Changes were saved successfully.');
        this.errors = {};
      } else this.errors = data;
      this.loading = false;
    }
  }
};
</script>
