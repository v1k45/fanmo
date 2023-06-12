<template>
<fm-card class="flex-grow pt-2 pb-6">
  <fm-form :errors="errors" @submit.prevent="$emit('donate-click', form)">

    <fm-input
      v-model.number="form.amount" class="mt-2" type="number" uid="amount" label="Select or enter an amount"
      required :min="minAmount" max="10000" placeholder="Enter an amount">
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

    <div class="flex flex-row space-x-2 mt-4">
      <div class="w-1/3">
        <fm-button class="flex justify-center" :loading="loading" block @click.prevent="$emit('cancel')">Cancel</fm-button>
      </div>
      <div class="w-2/3">
        <fm-button type="primary" native-type="submit" :loading="loading" block>Unlock Post</fm-button>
      </div>
    </div>
  </fm-form>
</fm-card>
</template>

<script>

export default {
  props: {
    user: { type: Object, required: true },
    post: { type: Object, required: false, default: null },
    loading: { type: Boolean, default: false }
  },
  data() {
    return {
      isMessageFocused: false,
      form: {
        amount: parseFloat(this.post.minimum_amount) || '',
        creator_username: this.user.username,
        message: '',
        post_id: this.post.id,
        is_hidden: false
      },
      errors: {}
    };
  },
  computed: {
    minAmount() {
      return this.post.minimum_amount;
    },
    presetAmounts() {
      return [25, 50, 100, 250, 500, 1000, 2500, 5000].filter(amount => amount >= this.minAmount);
    }
  },
  methods: {
    reset() {
      this.form = {
        amount: '',
        creator_username: this.user.username,
        post_id: this.post.id,
        message: '',
        is_hidden: false
      };
    }
  }
};
</script>
