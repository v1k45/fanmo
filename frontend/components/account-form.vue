<template>
<div class="max-w-md mt-4">
  <form @submit.prevent="donate">

    <div v-if="bank_account && bank_account.status == 'linked'" class="alert alert-success shadow my-4">
      <icon-check-circle class="mr-3"></icon-check-circle>
      Your bank details have been verified and you're all set to accept payments!
    </div>
    <div v-else-if="bank_account && bank_account.status == 'processing'" class="alert alert-info shadow my-4">
      <icon-loader-2 class="mr-3 animate-spin"></icon-loader-2>
      Your bank details are being verified. We'll send you an email when it is ready!
    </div>

    <error-alert :errors="errors"></error-alert>

    <div class="form-control">
      <label class="label label-text">Name (as it appears on bank account)</label>
      <input
        v-model="form.account_name"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.account_name }"
        :disabled="bank_account != null"
        required>
      <label
        v-for="(error, index) in errors.account_name"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Account Number</label>
      <input
        v-model="form.account_number"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.account_number }"
        :disabled="bank_account != null"
        required>
      <label
        v-for="(error, index) in errors.account_number"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">IFSC Code</label>
      <input
        v-model="form.ifsc"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.ifsc }"
        :disabled="bank_account != null"
        required>
      <label
        v-for="(error, index) in errors.ifsc"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Beneficiary Name</label>
      <input
        v-model="form.beneficiary_name"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.beneficiary_name }"
        :disabled="bank_account != null"
        required>
      <label
        v-for="(error, index) in errors.beneficiary_name"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Beneficiary Type</label>
      <select
        v-model="form.account_type"
        type="text"
        class="select select-bordered"
        :class="{ 'input-error': errors.account_type }"
        :disabled="bank_account != null"
        required>
        <option disabled value="">Please select one</option>
        <option>Individual</option>
        <option>Private Limited</option>
        <option>LLP</option>
        <option>Partnership</option>
        <option>Proprietorship</option>
      </select>
      <label
        v-for="(error, index) in errors.account_type"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Mobile Number</label>
      <input
        v-model="form.mobile_number"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.mobile_number }"
        :disabled="bank_account != null"
        required>
      <label
        v-for="(error, index) in errors.mobile_number"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <button v-if="bank_account == null" class="mt-4 btn btn-block btn-success">Submit for verification</button>

  </form>
</div>
</template>

<script>
import errorAlert from './ui/error-alert.vue';
export default {
  components: { errorAlert },
  data() {
    return {
      bank_account: null,
      form: {
        account_name: '',
        account_number: '',
        ifsc: '',
        beneficiary_name: '',
        account_type: '',
        mobile_number: ''
      },
      errors: {}
    };
  },
  async fetch() {
    const bankAccounts = await this.$axios.$get('/api/accounts/');
    if (bankAccounts.count) {
      this.canEdit = true;
      this.bank_account = bankAccounts.results[0];
      this.form = this.bank_account;
    }
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
