<template>
<div class="max-w-lg gy-4">
  <div class="card compact border shadow-lg">
    <div class="flex justify-between items-center p-4">
      <div class="flex items-center">
        <div v-if="donation.fan_user" class="avatar">
          <div class="w-11 h-11 border rounded-full">
            <img :src="donation.fan_user.avatar.small">
          </div>
        </div>
        <div v-else class="avatar placeholder">
          <div class="w-11 h-11 rounded-full bg-neutral-focus text-neutral-content">
            <span class="text-3xl">?</span>
          </div>
        </div>
        <div class="ml-3">
          <div v-if="donation.is_anonymous || donation.fan_user == null" class="text-xl font-bold">{{ donation.name }}</div>
          <div v-else class="text-xl font-bold">{{ donation.fan_user.username }}</div>
          <div class="text-xs text-base-content text-opacity-40">{{ donation.created_at }}</div>
        </div>
      </div>
      <div class="ml-3">
        <div class="flex text-2xl items-center">
          <icon-indian-rupee
            class="mr-2"
            :size="16"></icon-indian-rupee>
          {{ donation.amount }}
        </div>
      </div>
    </div>
    <div v-if="donation.message" class="card-body whitespace-pre-wrap">{{ donation.message }}</div>
  </div>
</div>
</template>

<script>
export default {
  props: {
    donation: {
      type: Object
    }
  },
  data() {
    return {
      step: 1,
      subscriptionForm: {
      },
      subscriptionErrors: {}
    };
  },
  methods: {
    async subscribe() {
      let subscription;
      try {
        subscription = await this.$axios.$post(
          '/api/subscriptions/',
          this.subscriptionForm
        );
      } catch (err) {
        this.subscriptionErrors = err.response.data;
        console.log(err.response.data);
        return;
      }

      const paymentOptions = subscription.payment_payload;
      paymentOptions.handler = (paymentResponse) => {
        this.processPayment(subscription, paymentResponse);
      };

      const rzp1 = new Razorpay(paymentOptions); // eslint-disable-line
      rzp1.open();
    },
    async processPayment(subscription, paymentResponse) {
      try {
        await this.$axios.$post('/api/payments/', {
          processor: 'razorpay',
          type: 'subscription',
          payload: paymentResponse
        });
      } catch (err) {
        console.error(err.response.data);
        this.subscriptionErrors.non_field_errors = [
          {
            message:
              'There was an error while processing the payment. If money was deducted from your account, it will be automatically refunded in 2 days. Feel free to contact us if you have any questions.'
          }
        ];
      }
    }
  }
};
</script>
