<template>
<fm-card class="flex-grow pt-2 pb-6">
  <div class="font-bold text-2xl">
    Donate
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
      required :min="user.preferences.minimum_amount" max="100000" placeholder="Enter an amount">
      <template #after-label>
        <div class="flex justify-between space-x-1 overflow-auto pb-1 mb-1">
          <button
            v-for="amount in presetAmounts" :key="amount" type="button"
            :title="`Donate ₹${amount}`"
            class="py-1 px-2 text-sm rounded border border-fm-primary-400 text-fm-primary-400 hover:border-fm-primary-500 hover:bg-fm-primary-500 hover:text-white"
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
      maxlength="3000" @focus="isMessageFocused = true;" @blur="isMessageFocused = false;">
    </fm-input>

    <div class="mt-4">
      <fm-input v-model="form.is_hidden" uid="is_hidden" type="checkbox" class="text-sm">
        Make this message visible only to the creator and me
      </fm-input>
    </div>

    <fm-button type="primary" native-type="submit" class="mt-4" :loading="loading" block>Support</fm-button>
  </fm-form>
</fm-card>
</template>

<script>
export default {
  props: {
    user: { type: Object, required: true },
    loading: { type: Boolean, default: false }
  },
  data() {
    return {
      isMessageFocused: false,
      form: {
        amount: '',
        creator_username: this.user.username,
        message: '',
        is_hidden: false
      },
      errors: {}
    };
  },
  computed: {
    presetAmounts() {
      return [25, 50, 100, 500, 1000, 2500, 5000].filter(amount => amount >= this.user.preferences.minimum_amount);
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
