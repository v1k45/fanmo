<template>
<div class="max-w-md flex-grow card compact sm:bg-white sm:shadow-lg border">
  <div class="card-body">
    <h1 class="font-extrabold text-3xl">
      Support me!
    </h1>
    <form class="mt-4" @submit.prevent="donate">
      <error-alert :errors="errors"></error-alert>

      <div v-if="step == 1" class="form-control">
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

      <div v-if="step == 2 && !$auth.loggedIn" class="form-control mb-3">
        <label class="label label-text">Name</label>
        <input
          v-model="form.name"
          type="text"
          class="input input-bordered"
          :class="{ 'input-error': errors.name }"
          placeholder="Anonymous">
        <label
          v-for="(error, index) in errors.name"
          :key="index"
          class="label">
          <span class="label-text-alt">{{ error.message }}</span>
        </label>
      </div>

      <!-- add email field to auto-register?  -->
      <div v-if="step === 2" class="form-control">
        <label class="label label-text">Message to {{ user.username }} (optional)</label>
        <textarea
          v-model="form.message"
          class="textarea textarea-bordered"
          :class="{ 'textarea-error': errors.message }"
          placeholder="Write something down...">
        </textarea>
        <label
          v-for="(error, index) in errors.message"
          :key="index"
          class="label">
          <span class="label-text-alt">{{ error.message }}</span>
        </label>
      </div>

      <div class="card-actions">
        <button v-if="step == 1" class="btn btn-block" type="button" @click.prevent="step = 2">Donate</button>
        <template v-if="step == 2">
          <button class="btn btn-ghost px-6 mr-3" type="button" @click="step = 1;">&larr; Back</button>
          <button class="btn flex-grow" type="submit">Pay <icon-indian-rupee class="max-h-4"></icon-indian-rupee>{{ form.amount }} </button>
        </template>
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
      step: 1,
      form: {
        amount: this.user.user_preferences.minimum_amount,
        username: this.user.username,
        name: '',
        message: '',
        is_anonymous: !this.$auth.loggedIn
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
