<template>
<div>

  <!-- tab start -->
  <div class="flex mt-2 mb-8 border-b-2 justify-center lg:justify-start">
    <button
      v-for="item in nav" :key="item.id"
      class="px-8 py-3 unstyled block relative font-medium text-black"
      :class="{ '!text-fm-primary font-bold': currentTab === item.id }" @click="currentTab = item.id">
      {{ item.label }}

      <div v-if="currentTab === item.id" class="absolute left-0 bottom-[-2px] w-full h-[2px] bg-fm-primary"></div>
    </button>
  </div>
  <!-- tab end -->

  <div class="md:px-8 container">

    <!-- general/account settings start -->
    <div v-show="currentTab === 'account'">

      <!-- username form start -->
      <fm-form class="max-w-md mx-auto lg:mx-0 mt-6" :errors="generalErrors" @submit.prevent="handleGeneralSubmit">
        <div class="text-xl font-medium text-black flex items-center mb-4">Page link</div>

        <fm-alert type="success" class="mt-4 text-sm">
          Your page is available at
          <a :href="`//${domainName}/${$auth.user.username}`" target="_blank">{{ `${domainName}/${$auth.user.username}` }}.</a>
        </fm-alert>

        <fm-input
          v-model="form.general.username" uid="username" class="mt-6"
          :placeholder="`${$auth.user.username}`"
          description="Changing your username will invalidate all the shared profile links that use your old username. Old username will also become claimable by other creators. We recommend not changing your username too often.">
          <template #prepend>
            {{ domainName }}/
          </template>
        </fm-input>

        <div class="text-left mt-8">
          <fm-button
            :type="hasUnsavedChanges.general ? 'primary' : ''"
            :disabled="!hasUnsavedChanges.general"
            :loading="isGeneralLoading" native-type="submit" block>
            Save changes
          </fm-button>
        </div>
      </fm-form>
      <!-- username form end -->

      <hr class="my-8">

      <!-- notification form start -->
      <fm-form class="max-w-md mx-auto lg:mx-0" :errors="notificationErrors" @submit.prevent="handleNotificationSubmit">
        <div class="text-xl font-medium text-black flex items-center mb-4">Notification preferences</div>
        <div class="mb-4 font-medium">Notify me for</div>

        <fm-input v-model="form.notification.notify_memberships" class="!mt-2" type="checkbox">Every new membership and renewal</fm-input>
        <fm-input v-model="form.notification.notify_donations" class="!mt-2" type="checkbox">Every donation</fm-input>
        <fm-input v-model="form.notification.notify_post_comments" class="!mt-2" type="checkbox">Comments on my posts</fm-input>
        <fm-input v-model="form.notification.notify_comment_replies" class="!mt-2" type="checkbox">Comment replies</fm-input>
        <fm-input v-model="form.notification.notify_following_posts" class="!mt-2" type="checkbox">Every new post from creators I follow</fm-input>
        <fm-input v-model="form.notification.notify_marketing" class="!mt-2" type="checkbox">Product updates and news</fm-input>

        <div class="text-left mt-6">
          <fm-button
            :type="hasUnsavedChanges.notification ? 'primary' : ''"
            :loading="isNotificationLoading" native-type="submit" block>
            Save preferences
          </fm-button>
        </div>
      </fm-form>
      <!-- notification form end -->

      <hr class="my-8">

      <!-- password form start -->
      <fm-form class="max-w-md mx-auto lg:mx-0" :errors="passwordErrors" @submit.prevent="handlePasswordSubmit">
        <div class="text-xl font-medium text-black flex items-center mb-4">Change password</div>
        <fm-input v-model="form.password.old_password" uid="old_password" type="password" label="Current password" required></fm-input>
        <fm-input v-model="form.password.new_password1" uid="new_password1" type="password" label="New password" required></fm-input>

        <div class="text-left mt-8">
          <fm-button
            :type="hasUnsavedChanges.password ? 'primary' : ''"
            :loading="isPasswordLoading" native-type="submit" block>
            Update password
          </fm-button>
        </div>
      </fm-form>
      <!-- password form end -->

      <hr class="my-8">

      <!-- email hypothetical form start -->
      <fm-form class="max-w-md mx-auto lg:mx-0" @submit.prevent>
        <div class="text-xl font-medium text-black flex items-center mb-4">Email</div>

        <div class="mb-6">
          <div class="mt-2 flex items-baseline">
            <span class="font-medium mr-2 break-all">{{ $auth.user.email }}</span>
            <span v-if="$auth.user.onboarding.checklist.email_verification" class="text-fm-success-600 text-sm ml-1 font-medium">(Verified)</span>
            <template v-else>
              <span class="text-fm-error ml-1 text-sm mr-2">(Unverified)</span>
              <nuxt-link :to="{ name: 'onboarding-verify' }" class="ml-auto text-sm flex-shrink-0">Verify now</nuxt-link>
            </template>
          </div>
        </div>

        <!-- TODO: someday, if needed? -->
        <!-- <fm-input label="New email" type="email" required></fm-input>
        <fm-input type="password" label="Password" required></fm-input>

        <div class="text-left mt-8">
          <fm-button :type="hasUnsavedChanges.password ? 'primary' : ''" native-type="submit" block>
            Update email
          </fm-button>
        </div> -->
      </fm-form>
      <!-- email hypothetical form end -->

    </div>
    <!-- general/account settings end -->

    <!-- bank account settings start -->
    <div v-show="currentTab === 'payment'">


      <div class="text-xl font-medium text-black flex items-center">Bank account details</div>

      <!-- verification status start -->
      <div class="max-w-lg">
        <fm-alert v-if="bankAccount && bankAccount.status == 'linked'" type="success" class="my-4">
          Your bank details have been verified and you're all set to accept payments!
        </fm-alert>
        <fm-alert v-else-if="bankAccount && bankAccount.status == 'processing'" class="my-4">
          Your bank details are being verified. We'll reach out to you within 2 business days.
        </fm-alert>
      </div>
      <!-- verification status end -->

      <!-- description start -->
      <div class="text-gray-500 mt-2 text-sm mb-4 max-w-xl">
        This will be used for making payouts to your bank account.
        <template v-if="bankAccount && bankAccount.status !== 'created'">
          <br>
          Once verified, you can start accepting payments from your supporters. <br>
          Verification process generally takes upto 2 working days.
        </template>
      </div>
      <!-- description end -->

      <!-- account static form start -->
      <fm-form v-if="bankAccount && bankAccount.status !== 'created'" class="max-w-md mx-auto lg:mx-0" :errors="accountErrors" @submit.prevent>
        <fm-input v-model="form.payment.account_name" uid="account_name" type="text" required readonly>
          <template #label>
            Name <span class="text-xs">(as it appears on the bank account)</span>
          </template>
        </fm-input>

        <fm-input :value="maskString(form.payment.account_number)" uid="account_number" label="Account number" type="text" readonly required></fm-input>
        <fm-input v-model="form.payment.ifsc" uid="ifsc" label="IFSC code" type="text" readonly required></fm-input>
        <fm-input v-model="form.payment.account_type" uid="account_type" label="Account type" type="select" readonly required>
          <option v-for="accountType in ACCOUNT_TYPES" :key="accountType" :value="accountType">
            {{ accountType }}
          </option>
        </fm-input>

        <fm-alert type="warning" class="mt-6">
          We do not support changing bank account details from this page for security reasons.
          Please reach out to us via email or the chat widget if you need any help.
        </fm-alert>
      </fm-form>
      <!-- account static form end -->

      <!-- no account action start -->
      <fm-card v-else class="max-w-lg overflow-hidden" body-class="bg-gray-100 text-center !pt-8 !pb-12">
        <icon-wallet class="h-16 w-16 stroke-1 animatecss animatecss-tada"></icon-wallet>
        <div class="mt-2">
          You haven't set up a bank account yet. Finish your account setup to start receiving payments.
        </div>
        <fm-button type="primary" class="mt-4" @click="continueOnboarding">Finish account setup &rarr;</fm-button>
      </fm-card>
      <!-- no account action end -->

    </div>
    <!-- bank account settings end -->

  </div>

</div>
</template>

<script>
import cloneDeep from 'lodash/cloneDeep';
import pick from 'lodash/pick';
import { mapActions, mapState } from 'vuex';
import { skipOnboarding, maskString } from '~/utils';

const ACCOUNT_TYPES = ['Individual', 'Private Limited', 'Partnership', 'Proprietorship', 'LLP'];

const initialFormState = (user = null) => ({
  general: {
    username: user ? (user.username || '') : ''
  },
  notification: {
    notify_memberships: true,
    notify_donations: true,
    notify_post_comments: true,
    notify_comment_replies: true,
    notify_following_posts: true,
    notify_marketing: true
  },
  password: {
    old_password: '',
    new_password1: ''
  },
  email: {
    new_email: '',
    password: ''
  },
  payment: {
    account_name: '',
    account_number: '',
    ifsc: '',
    account_type: ''
  }
});
export default {
  data() {
    return {
      maskString,
      currentTab: 'account',
      nav: [
        { id: 'account', label: 'Account' },
        { id: 'payment', label: 'Payment' }
      ],

      ACCOUNT_TYPES,
      domainName: location.host,
      form: initialFormState(this.$auth.user),
      isGeneralLoading: false,
      isNotificationLoading: false,
      isPasswordLoading: false,
      isAccountLoading: false,
      generalErrors: {},
      notificationErrors: {},
      passwordErrors: {},
      accountErrors: {}
    };
  },
  computed: {
    ...mapState('users', ['accounts']),
    hasUnsavedChanges() {
      return {
        general: this.form.general.username !== this.$auth.user.username,
        notification: Object.entries(this.form.notification).some(([key, val]) => this.$auth.user.preferences[key] !== val),
        password: Object.values(this.form.password).some(val => !!val),
        email: Object.values(this.form.email).some(val => !!val)
      };
    },
    bankAccount() {
      if (!this.accounts || !this.accounts.count) return null;
      return this.accounts.results[0];
    }
  },
  watch: {
    '$auth.user': {
      immediate: true,
      deep: true,
      handler(user) {
        this.form.general.username = user.username;
        Object.assign(this.form.notification, pick(user.preferences, Object.keys(initialFormState().notification)));
      }
    },
    accounts: {
      immediate: true,
      handler(accounts) {
        if (!accounts || !accounts.count || !accounts.results.length) return;
        Object.assign(this.form.payment, pick(accounts.results[0], Object.keys(initialFormState().payment)));
      }
    }
  },
  created() {
    this.loadAccounts();
  },
  methods: {
    ...mapActions('users', ['loadAccounts', 'updateSelfUser', 'updatePassword']),
    async handleGeneralSubmit() {
      try {
        await this.$confirm.error([
          '<span class="text-sm">Changing your username will invalidate all the shared profile links that use your old username. <br><br>',
          'Old username will also become claimable by other creators. We recommend not changing your username too often. <br><br></span>',
          '<strong>Do you want to proceed with this action?</strong><br><br>'
        ].join(' '), 'Confirm', { html: true });
      } catch (err) {
        return;
      }
      this.isGeneralLoading = true;
      const payload = cloneDeep(this.form.general);

      const { success, data } = await this.updateSelfUser(payload);

      if (success) {
        this.$toast.success('Your changes were saved successfully.');
        this.generalErrors = {};
      } else this.generalErrors = data;
      this.isGeneralLoading = false;
    },
    async handlePasswordSubmit() {
      this.isPasswordLoading = true;

      const payload = cloneDeep(this.form.password);
      payload.new_password2 = payload.new_password1;

      const { success, data } = await this.updatePassword(payload);

      if (success) this.$toast.success('Your password was updated successfully.');
      else this.passwordErrors = data;

      this.form.password = initialFormState().password;

      this.isPasswordLoading = false;
    },
    async handleNotificationSubmit() {
      this.isNotificationLoading = true;
      const { success, data } = await this.updateSelfUser({ preferences: this.form.notification });
      if (success) this.$toast.success('Your changes were saved successfully.');
      else this.notificationErrors = data;
      this.isNotificationLoading = false;
    },
    continueOnboarding() {
      skipOnboarding.unset(this.$auth.user.username);
      this.$router.push({ name: 'onboarding-payment-info' });
    }
  }
};
</script>
