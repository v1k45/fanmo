<template>
<fm-card class="flex-grow pt-2 pb-6">
  <div class="font-bold text-2xl">
    Tip
  </div>
  <fm-form class="mt-4" :errors="errors" @submit.prevent="$emit('donate-click', form)">

    <div>
      <template v-if="user.preferences.donation_description">{{ user.preferences.donation_description }}</template>
      <template v-else>
        Show your appreciation for <strong>{{ user.name || user.username }}</strong> with a one time payment.
      </template>
    </div>

    <hr class="my-4">

    <fm-input
      v-model.number="form.amount" class="mt-2" type="number" uid="amount" label="Select or enter an amount"
      required :min="user.preferences.minimum_amount" max="10000" placeholder="Enter an amount">
      <template #after-label>
        <div class="flex justify-between space-x-1 overflow-auto pb-1 mb-1">
          <button
            v-for="amount in presetAmounts" :key="amount" type="button"
            :title="`Tip ₹${amount}`"
            class="py-1 px-2 text-sm rounded border border-fm-primary-400 hover:border-fm-primary-500 hover:bg-fm-primary-500 hover:text-white"
            :class="{'border-fm-primary-500 bg-fm-primary-500 text-white': amount == form.amount, 'text-fm-primary-400': amount !== form.amount}"
            @click="form.amount = amount;">
            {{ $currency(amount) }}
          </button>
        </div>
      </template>
      <template #prepend>₹</template>
    </fm-input>

    <fm-input
      v-model="form.message" uid="message" type="textarea" label="Message (optional)"
      placeholder="Say something nice" :rows="form.message || isMessageFocused ? 3 : 1"
      maxlength="500" @focus="isMessageFocused = true;" @blur="isMessageFocused = false;">
      <template #label>
        <div class="flex justify-between">
          <div>Message (optional)</div>
          <div v-if="(user.preferences.enable_donation_tiers && tier)" v-tooltip="tier.style.label" class="text-sm flex items-center space-x-2" :class="{'text-fm-error': messageLength.used > tier.max_length}">
            <component :is="tier.style.icon" v-if="tier.name" class="h-em w-em"></component>
            <span>{{ messageLength.used }}/{{ tier.max_length }}</span>
          </div>
        </div>
        <div v-if="user.preferences.enable_donation_tiers && tier" class="w-full bg-gray-200 h-0.5 rounded mt-1">
          <div class="bg-fm-primary rounded h-0.5" :style="{width: `${messageLength.percent}%`}"></div>
        </div>
      </template>
    </fm-input>

    <template v-if="user.preferences.enable_donation_tiers && messageLength.used">
      <div v-if="!tier" class="text-fm-error text-xs mt-1"><icon-info class="h-em w-em"></icon-info> Please tip at least ₹50 to include a message.</div>
      <div v-else-if="(messageLength.used > tier.max_length && tier.max_length !== 300)" class="text-fm-error text-xs mt-1"><icon-info class="h-em w-em"></icon-info> Message is too long, increase tip amount to send a larger message.</div>
    </template>

    <div class="mt-4">
      <fm-input v-model="form.is_hidden" uid="is_hidden" type="checkbox" class="text-sm">
        Make this message visible only to the creator and me
      </fm-input>
    </div>

    <fm-button type="primary" native-type="submit" class="btn-donate mt-4" :loading="loading" block>Support</fm-button>
  </fm-form>
</fm-card>
</template>

<script>
import { DONATION_TIER_STYLE_MAP } from '~/utils';

export default {
  props: {
    user: { type: Object, required: true },
    loading: { type: Boolean, default: false }
  },
  data() {
    return {
      isMessageFocused: false,
      form: {
        amount: parseFloat(this.user.preferences.default_donation_amount) || '',
        creator_username: this.user.username,
        message: '',
        is_hidden: false
      },
      errors: {}
    };
  },
  computed: {
    presetAmounts() {
      return [25, 50, 100, 250, 500, 1000, 2500, 5000].filter(amount => amount >= this.user.preferences.minimum_amount);
    },
    tier() {
      const amount = this.form.amount || 0;
      const tiers = [...this.user.donation_tiers].reverse().map(t => ({ ...t, min_amount: parseFloat(t.min_amount), style: DONATION_TIER_STYLE_MAP[t.name] }));
      return tiers.find(t => amount >= t.min_amount);
    },
    messageLength() {
      const used = this.form.message.length;
      let percent = 100;
      if (this.tier && this.tier.max_length >= used) percent = ((used * 100) / this.tier.max_length);
      return { used, percent };
    }
  },
  created() {
  },
  methods: {
    reset() {
      this.form = {
        amount: '',
        creator_username: this.user.username,
        message: '',
        is_hidden: false
      };
    }
  }
};
</script>
