<template>
<div class="md:px-8 container">

  <!-- general form start -->
  <fm-form class="max-w-md mx-auto lg:mx-0 mt-6" :errors="generalErrors" @submit.prevent="handleGeneralSubmit">
    <div class="text-xl font-medium text-black flex items-center mb-4">General</div>

    <fm-input v-model="form.general.name" uid="name" label="Name"></fm-input>
    <fm-input v-model="form.general.avatar_base64" uid="avatar_base64" label="Profile picture" type="file" accept="images/*"></fm-input>

    <div class="text-left mt-8">
      <fm-button
        :type="hasUnsavedChanges.general ? 'primary' : ''"
        :loading="isGeneralLoading" native-type="submit" block>
        Save changes
      </fm-button>
    </div>
  </fm-form>
  <!-- general form end -->

  <hr class="my-8">

  <!-- notification form start -->
  <fm-form class="max-w-md mx-auto lg:mx-0" :errors="notificationErrors" @submit.prevent="handleNotificationSubmit">
    <div class="text-xl font-medium text-black flex items-center mb-4">Notification preferences</div>
    <div class="mb-4 font-medium">Notify me for</div>
    <fm-input v-model="form.notification.notify_following_posts" class="!mt-3" type="checkbox">Every new post from creators I follow</fm-input>
    <fm-input v-model="form.notification.notify_comment_replies" class="!mt-3" type="checkbox">Comment replies</fm-input>
    <fm-input v-model="form.notification.notify_marketing" class="!mt-3" type="checkbox">Product updates and news</fm-input>

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

  <hr class="my-8">

  <div class="max-w-md">
    <div class="text-xl font-medium text-black flex items-center mb-4">Become a creator</div>

    <div class="mt-4"></div>

    <fm-card class="max-w-lg overflow-hidden" body-class="bg-gray-100 text-center !pt-8 !pb-12">
      <logo circle class="h-16 w-16 animatecss animatecss-tada inline-block mr-6"></logo>
      <div class="mt-2">
        Start offering memberships and accepting donations on Fanmo.
        It takes less than 5 minutes to get started!
      </div>
      <fm-button type="primary" block class="mt-4" @click="restartOnboarding">Become a creator &rarr;</fm-button>
    </fm-card>

  </div>

</div>
</template>

<script>
import cloneDeep from 'lodash/cloneDeep';
import pick from 'lodash/pick';
import { mapActions } from 'vuex';
import { getBase64FromFile, skipOnboarding } from '~/utils';

const initialFormState = (user = null) => ({
  general: {
    name: user ? (user.name || '') : '',
    avatar_base64: user ? (user.avatar ? user.avatar.full : '') : ''
  },
  notification: {
    notify_following_posts: true,
    notify_comment_replies: true,
    notify_marketing: true
  },
  password: {
    old_password: '',
    new_password1: ''
  },
  email: {
    new_email: '',
    password: ''
  }
});
export default {
  data() {
    return {
      form: initialFormState(this.$auth.user),
      isGeneralLoading: false,
      isNotificationLoading: false,
      isPasswordLoading: false,
      generalErrors: {},
      notificationErrors: {},
      passwordErrors: {}
    };
  },
  computed: {
    hasUnsavedChanges() {
      return {
        general: (
          this.form.general.name !== this.$auth.user.name ||
          (
            this.$auth.user.avatar
              ? this.form.general.avatar_base64 !== this.$auth.user.avatar.full
              : this.form.general.avatar_base64 !== '')
        ),
        notification: Object.entries(this.form.notification).some(([key, val]) => this.$auth.user.preferences[key] !== val),
        password: Object.values(this.form.password).some(val => !!val),
        email: Object.values(this.form.email).some(val => !!val)
      };
    }
  },
  watch: {
    '$auth.user': {
      immediate: true,
      deep: true,
      handler(user) {
        this.form.general.name = user.name;
        this.form.general.avatar_base64 = user.avatar ? user.avatar.full : '';

        Object.assign(this.form.notification, pick(user.preferences, Object.keys(initialFormState().notification)));
      }
    }
  },
  methods: {
    ...mapActions('users', ['updateSelfUser', 'updatePassword']),
    async handleGeneralSubmit() {
      this.isGeneralLoading = true;
      const payload = cloneDeep(this.form.general);
      // adding new
      if (payload.avatar_base64 && typeof payload.avatar_base64 !== 'string') payload.avatar_base64 = await getBase64FromFile(payload.avatar_base64);
      // deleting existing
      // eslint-disable-next-line brace-style
      else if (this.$auth.user.avatar && !payload.avatar_base64) { /* nothing. send falsy value as is. */ }
      // unchanged
      else delete payload.avatar_base64;

      const { success, data } = await this.updateSelfUser(payload);

      if (success) this.$toast.success('Your changes were saved successfully.');
      else this.generalErrors = data;
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
    restartOnboarding() {
      skipOnboarding.unset(this.$auth.user.id);
      this.$router.push({ name: 'onboarding-role' });
    }
  }
};
</script>
