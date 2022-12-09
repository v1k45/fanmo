<template>
<div>
  <div class="max-w-lg mx-auto lg:mx-0">
    <fm-form :errors="errors" @submit.prevent="save">
      <fm-input
        v-model.number="form.minimum_amount" type="number" uid="amount" label="Minimum amount"
        description="The minimum amount your supporters can tip you."
        min="1" max="10000" placeholder="Enter an amount">
        <template #prepend>₹</template>
      </fm-input>

      <fm-input
        v-model.number="form.default_donation_amount" type="number" uid="amount" label="Default amount"
        description="This amount will be selected by default on the tip widget. Clear the field to not select a default tip value."
        :min="$auth.user.preferences.minimum_amount" max="10000" placeholder="Enter an amount">
        <template #after-label>
          <div class="flex justify-between space-x-1 overflow-auto pb-1 mb-1">
            <button
              v-for="amount in presetAmounts" :key="amount" type="button"
              class="py-1 px-2 text-sm rounded border border-fm-primary-400 hover:border-fm-primary-500 hover:bg-fm-primary-500 hover:text-white"
              :class="{'border-fm-primary-500 bg-fm-primary-500 text-white': parseFloat(amount) === parseFloat(form.default_donation_amount), 'text-fm-primary-400': parseFloat(amount) !== parseFloat(form.default_donation_amount)}"
              @click="form.default_donation_amount = amount;">
              {{ $currency(amount) }}
            </button>
          </div>
        </template>
        <template #prepend>₹</template>
      </fm-input>

      <fm-input v-model="form.enable_donation_tiers" type="checkbox">
        Enable tipping tiers
      </fm-input>
      <div class="text-gray-500 text-sm">
        Give perks to generous supporters who tip higher. When enabled, higher tips will get to send larger tip messages. <a href="" @click.prevent="tippingTiersVisible = true">Click here to know more.</a>
      </div>

      <hr class="my-8">

      <fm-input
        v-model="form.donation_description" :disabled="loading"
        uid="preferences.donation_description" type="textarea" rows="4" label="Description"
        class="mt-6"
        description="This will be shown in the tip widget. Tell your audience how their support will help you."
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
          <div class="text-sm text-gray-500 mt-1">This will be shown to your supporters after they tip. A copy will also be sent to their email.</div>
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
    is-preview
    show-close>
  </profile-payment-success>
  <!-- nested dialog end -->

  <!-- badge dialog start -->
  <fm-dialog v-model="tippingTiersVisible">
    <template #header><div class="text-base">Tipping tiers</div></template>
    <div>
      <div>
        Give perks to your generous supporters who tip you higher than others.
        Based on the amount they tip, they will get to send larger tip messages and also get a special badge next to their tip.
      </div>
      <div class="mt-2">
        Supporters who tip less than {{ $currency("50") }} won't get to send a message along with their tip.
      </div>
      <table class="table-fixed w-full text-center my-4">
        <thead>
          <tr>
            <th>Minimum Amount</th>
            <th>Level</th>
            <th>Message Length</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tier in tiers" :key="tier.name">
            <td>{{ $currency(tier.min_amount) }}</td>
            <td><div class="rounded-lg text-white" :class="tier.style.css"><component :is="tier.style.icon" class="h-em w-em"></component> {{ tier.style.label }}</div></td>
            <td>{{ tier.max_length }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </fm-dialog>
  <!-- badge dialog end -->
</div>
</template>

<script>
import random from 'lodash/random';
import { mapActions } from 'vuex';
import { DONATION_TIER_STYLE_MAP } from '~/utils';

export default {
  data() {
    return {
      random,
      loading: false,
      isPaymentSuccessPreviewVisible: false,
      tippingTiersVisible: false,
      form: {
        minimum_amount: '',
        enable_donation_tiers: '',
        default_donation_amount: '',
        donation_description: '',
        thank_you_message: ''
      },
      errors: {}
    };
  },
  head: {
    title: 'Tip Settings'
  },
  computed: {
    donationData() {
      return this.isPaymentSuccessPreviewVisible ? { amount: random(50, 2000) } : { amount: 0 };
    },
    presetAmounts() {
      return [25, 50, 100, 250, 500, 1000, 2500, 5000].filter(amount => amount >= this.$auth.user.preferences.minimum_amount);
    },
    tiers() {
      return this.$auth.user.donation_tiers.map(t => ({ ...t, style: DONATION_TIER_STYLE_MAP[t.name] }));
    }
  },
  watch: {
    '$auth.user.preferences': {
      immediate: true,
      handler(preferences) {
        this.form = {
          minimum_amount: preferences.minimum_amount,
          enable_donation_tiers: preferences.enable_donation_tiers,
          default_donation_amount: preferences.default_donation_amount,
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
