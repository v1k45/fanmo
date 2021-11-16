<template>
<div>
  <h1 class="text-2xl font-bold">Settings</h1>

  <div class="tabs mt-6">
    <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.ACCOUNT }" @click="activeTab = tabName.ACCOUNT;">Account settings</div>
    <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.SOCIAL }" @click="activeTab = tabName.SOCIAL;">Social platforms</div>
    <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.PAYMENT }" @click="activeTab = tabName.PAYMENT;">
      Payment details
    </div>
    <div class="tab tab-lg tab-lifted flex-grow cursor-default"></div>
  </div>

  <form v-show="activeTab === tabName.ACCOUNT" class="max-w-md mt-4" @submit.prevent>
    <div class="form-control">
      <label class="label label-text">Name</label>
      <input type="text" class="input input-bordered">
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Username</label>
      <input type="text" class="input input-bordered">
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">About you</label>
      <textarea rows="4" class="textarea textarea-bordered"></textarea>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Website</label>
      <input type="text" class="input input-bordered" placeholder="https://example.com">
    </div>
  </form>

  <form v-show="activeTab === tabName.SOCIAL" class="max-w-md" @submit.prevent>
    <div
      v-for="social in ['Facebook', 'Twitter', 'Instagram', 'Reddit', 'YouTube', 'Twitch']" :key="social" class="form-control mt-3">
      <label class="label label-text">{{ social }}</label>
      <input type="text" class="input input-bordered">
    </div>
  </form>

  <account-form v-show="activeTab == tabName.PAYMENT"></account-form>

  <form v-show="activeTab === tabName.PAYMENT && false" class="max-w-md mt-4" @submit.prevent>
    <div class="alert alert-success shadow">
      <icon-check-circle class="mr-3"></icon-check-circle>
      Your bank details have been verified and you're all set to accept payments!
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Name (as it appears on bank account)</label>
      <input type="text" class="input input-bordered">
    </div>
    <div class="form-control mt-3">
      <label class="label label-text">Bank</label>
      <select class="select select-bordered"></select>
    </div>
    <div class="form-control mt-3">
      <label class="label label-text">Account number</label>
      <input type="text" class="input input-bordered">
    </div>
    <div class="form-control mt-3">
      <label class="label label-text">IFSC code</label>
      <input type="text" class="input input-bordered">
    </div>

    <button class="mt-8 btn btn-block btn-success">Submit for verification</button>
  </form>

</div>
</template>

<script>
import accountForm from '../components/account-form.vue';
export default {
  components: { accountForm },
  data() {
    const tabName = {
      ACCOUNT: 'account',
      SOCIAL: 'social',
      PAYMENT: 'payment'
    };
    return {
      tabName,
      activeTab: tabName.ACCOUNT
    };
  },
  head: {
    title: 'Settings'
  }
};
</script>
