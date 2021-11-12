<template>
<div class="max-w-md flex-grow card sm:bg-white sm:shadow-lg border">
  <div class="card-body">
    <h1 class="font-extrabold text-3xl">
      Support {{ user.username }}
    </h1>
    <div class="font-medium mt-3">
      Subtile
    </div>

    <form class="mt-6" @submit.prevent="donate">
      <error-alert :errors="errors"></error-alert>
      <div class="form-control">
        <label class="label label-text">Donate with any amount you like</label>
        <input
          v-model="form.amount"
          type="number"
          class="input input-bordered"
          :class="{ 'input-error': errors.amount }"
          required>
        <label
          v-for="(error, index) in errors.amount"
          :key="index"
          class="label">
          <span class="label-text-alt">{{ error.message }}</span>
        </label>
      </div>
      <div class="justify-center card-actions">
        <button class="btn btn-block">Pay</button>
      </div>
    </form>
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
    }
  },
  data() {
    return {
      form: {
        amount: this.user.user_preferences.minimum_amount,
        username: this.user.username
      },
      errors: {}
    };
  },
  methods: {
    async donate() {
      let donation;
      try {
        donation = await this.$axios.$post(
          '/api/donations/',
          this.form
        );
      } catch (err) {
        this.errors = err.response.data;
        console.log(err.response.data);
        return;
      }

      const paymentOptions = donation.payment_payload;
      paymentOptions.handler = (paymentResponse) => {
        this.processPayment(donation, paymentResponse);
      };

      const rzp1 = new Razorpay(paymentOptions); // eslint-disable-line
      rzp1.open();
    },
    async processPayment(donation, paymentResponse) {
      try {
        await this.$axios.$post('/api/payments/', {
          processor: 'razorpay',
          type: 'donation',
          payload: paymentResponse
        });
      } catch (err) {
        console.error(err.response.data);
        this.errors.non_field_errors = [
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
