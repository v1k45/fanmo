<template>
<div>
  <h1 class="text-2xl font-bold">Settings</h1>

  <div class="tabs mt-6">
    <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.PROFILE }" @click="activeTab = tabName.PROFILE;">Profile</div>
    <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.LINKS }" @click="activeTab = tabName.LINKS;">Links</div>
    <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.PAYMENT }" @click="activeTab = tabName.PAYMENT;">
      Payment details
    </div>
    <div class="tab tab-lg tab-lifted flex-grow cursor-default"></div>
  </div>

  <general-settings v-show="activeTab === tabName.PROFILE"></general-settings>

  <link-settings v-show="activeTab === tabName.LINKS"></link-settings>

  <account-form v-show="activeTab == tabName.PAYMENT"></account-form>

</div>
</template>

<script>
export default {
  layout: 'with-sidebar',
  data() {
    const tabName = {
      PROFILE: 'profile',
      LINKS: 'links',
      PAYMENT: 'payment'
    };
    return {
      tabName,
      activeTab: tabName.PROFILE
    };
  },
  head: {
    title: 'Settings'
  }
};
</script>
