<template>
<main class="sm:py-16 bg-gray-50 min-h-screen">
  <logo class="h-8 mx-auto"></logo>
  <div class="max-w-lg mx-auto mt-10">
    <fm-wizard>
      <fm-wizard-step id="1" finished><span class="text-sm">Create account</span></fm-wizard-step>
      <fm-wizard-step id="2" finished><span class="text-sm">Complete profile</span></fm-wizard-step>
      <fm-wizard-step id="3" current><span class="text-sm">Add payment details</span></fm-wizard-step>
    </fm-wizard>
  </div>
  <fm-card class="max-w-lg mx-auto py-4 sm:px-4 mt-4 relative">
    <button
      class="absolute left-4 top-4 text-black"
      title="Back to profile information" @click="$router.push({ name: 'onboarding-profile-info' })">
      <icon-arrow-left></icon-arrow-left>
    </button>
    <div class="max-w-sm mx-auto">

      <h1 class="font-title font-bold text-2xl text-center mb-6">Where do we send your money?</h1>
      <fm-form :errors="errors" @submit.prevent="setPaymentInfo">

        <fm-input v-model="form.account_name" uid="account_name" type="text" required autofocus>
          <template #label>
            Name <span class="text-xs">(as it appears on the bank account)</span>
          </template>
        </fm-input>

        <fm-input v-model="form.account_number" uid="account_number" label="Account number" type="text" required></fm-input>
        <fm-input v-model="form.ifsc" uid="ifsc" label="IFSC code" type="text" required></fm-input>
        <fm-input v-model="form.account_type" uid="account_type" label="Account type" type="select" required>
          <option v-for="accountType in ACCOUNT_TYPES" :key="accountType" :value="accountType">
            {{ accountType }}
          </option>
        </fm-input>

        <fm-button native-type="submit" type="primary" size="lg" class="mt-8" :disabled="loading" block>Finish</fm-button>
        <fm-button
          native-type="button" type="link" size="lg" class="mt-4 mb-6" block
          @click="skipForNow">
          Skip for now
        </fm-button>


      </fm-form>
    </div>

  </fm-card>

  <fm-dialog v-model="reviewDialog.isVisible" dialog-class="md:w-[28rem]">
    <template #header>
      <div class="flex items-center">
        <icon-check-square class="h-6 w-6 mr-2 text-fm-success-600 inline-block"></icon-check-square> Review your account details
      </div>
    </template>

    <div class="text-sm">Page name</div>
    <div class="font-medium text-black">{{ $auth.user.name }}</div>

    <div class="text-sm mt-4">Full name</div>
    <div class="font-medium text-black">{{ $auth.user.onboarding.full_name }}</div>

    <div class="text-sm mt-4">Account name</div>
    <div class="font-medium text-black">{{ form.account_name }}</div>

    <div class="text-sm mt-4">Account number</div>
    <div class="font-medium text-black">{{ form.account_number }}</div>

    <div class="text-sm mt-4">IFSC code</div>
    <div class="font-medium text-black">{{ form.ifsc }}</div>

    <div class="text-sm mt-4">Account type</div>
    <div class="font-medium text-black mt-1">{{ form.account_type }}</div>


    <template #footer>
      <div class="text-right">
        <fm-button @click="reviewDialog.isVisible = false;">Go back</fm-button>
        <fm-button type="primary" @click="submitForReview">Submit</fm-button>
      </div>
    </template>
  </fm-dialog>
</main>
</template>

<script>
import get from 'lodash/get';
import pick from 'lodash/pick';
import { CheckSquare as IconCheckSquare } from 'lucide-vue';
import { skipOnboarding } from '~/utils';

const ACCOUNT_TYPES = ['Individual', 'Private Limited', 'Partnership', 'Proprietorship', 'LLP'];

const initialState = () => {
  return {
    loading: false,
    accountId: null,
    form: {
      account_name: '',
      account_number: '',
      account_type: '',
      ifsc: ''
    },
    errors: {},
    reviewDialog: {
      isVisible: false
    }
  };
};
export default {
  components: {
    IconCheckSquare
  },
  layout: 'empty',
  data() {
    return {
      ACCOUNT_TYPES,
      ...initialState()
    };
  },
  head: {
    title: 'Payment information'
  },
  created() {
    this.getExistingAccount();
  },
  methods: {
    async getExistingAccount() {
      this.loading = true;
      try {
        const data = await this.$axios.$get('/api/accounts/');
        const existingAccount = get(data, 'results[0]', null);
        if (!existingAccount) return;
        this.accountId = existingAccount.id;
        this.form = pick(existingAccount, Object.keys(this.form));
      } catch (err) {
        this.errors = err.response.data;
      } finally {
        this.loading = false;
      }
    },
    async setPaymentInfo() {
      try {
        if (this.accountId) await this.$axios.$patch(`/api/accounts/${this.accountId}/`, this.form);
        else await this.$axios.$post('/api/accounts/', this.form);
        await this.$auth.fetchUser();
        this.errors = {};
        this.$toast.info('Your payment information was saved successfully!');
        this.reviewDialog.isVisible = true;
      } catch (err) {
        this.errors = err.response.data;
      }
    },
    async submitForReview() {
      this.reviewDialog.isVisible = false;
      try {
        const user = await this.$axios.$patch('/api/me/', { onboarding: { submit_for_review: true } });
        this.$auth.setUser(user);
        this.errors = {};
        this.$toast.success('Your information has been submitted. We will get back to you within 2 business days!');
        this.$router.push('/');
      } catch (err) {
        this.errors = err.response.data;
      }
    },
    skipForNow() {
      skipOnboarding.set(this.$auth.user.username);
      this.$router.push('/');
    }
  }
};
</script>
