<template>
<div class="col-12 sm:col-6 md:col-6 lg:col-4 xl:col-3 gy-4">
  <div class="card compact border shadow-lg">
    <figure v-if="step == 1">
      <img src="https://picsum.photos/200/100">
    </figure>
    <div v-if="step == 1" class="card-body">
      <h2 class="card-title text-center">
        <icon-indian-rupee class="inline h-6"></icon-indian-rupee>{{ tier.amount }}
        <div class="text-base truncate">{{ tier.name }}</div>
      </h2>
      <p class="mt-2">{{ tier.description }}</p>
      <ul class="list-disc list-inside text-left mt-3">
        <li v-for="(benefit, index) in tier.benefits" :key="index">
          {{ benefit }}
        </li>
      </ul>
      <div class="justify-center card-actions">
        <button class="btn btn-block" @click="step = 2">Subscribe</button>
      </div>
    </div>
    <div v-if="step == 2" class="card-body">
      <h2 class="card-title text-center">
        <icon-indian-rupee class="inline h-6"></icon-indian-rupee>{{ tier.amount }}
        <div class="text-base truncate">{{ tier.name }}</div>
      </h2>
      <form class="mt-6" @submit.prevent="subscribe">
        <error-alert :errors="subscriptionErrors"></error-alert>
        <div class="form-control">
          <label class="label label-text">Subscribe with any amount you like</label>
          <input
            v-model="subscriptionForm.amount"
            type="number"
            class="input input-bordered"
            :class="{ 'input-error': subscriptionErrors.amount }"
            required>
          <label
            v-for="(error, index) in subscriptionErrors.amount"
            :key="index"
            class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <div class="justify-center card-actions">
          <button class="btn btn-block" @click="subscribe">Pay</button>
        </div>
      </form>
    </div>
  </div>
</div>
</template>

<script>
import errorAlert from './ui/error-alert.vue';
export default {
  components: { errorAlert },
  props: {
    user: {
      type: Object
    },
    tier: {
      type: Object
    }
  },
  data() {
    return {
      step: 1,
      subscriptionForm: {
        username: this.user.username,
        amount: this.tier.amount
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
