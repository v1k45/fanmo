<template>
<div class="max-w-xl gy-4">
  <div class="card compact border shadow-lg">
    <div class="flex justify-between items-center p-4">
      <div class="flex items-center">
        <div class="avatar">
          <div class="w-11 h-11 border rounded-full">
            <img src="https://picsum.photos/100/100">
          </div>
        </div>
        <div class="ml-3">
          <div class="text-xl font-bold">{{ post.title }}</div>
          <div class="text-xs text-base-content text-opacity-40">10 Jul, 2012 9PM</div>
        </div>
      </div>
      <div class="ml-3">
        <div class="flex text-2xl items-center">
          <!-- context menu to flag/report/delete -->
        </div>
      </div>
    </div>
    <div v-if="post.content" class="card-body">
      {{ post.content.text }}
    </div>
    <div v-else class="card-body">
      Locked! {{ post.visibility }}
    </div>
  </div>
</div>
</template>

<script>
export default {
  props: {
    post: {
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
