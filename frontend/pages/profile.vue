<template>
<div v-if="user != null">
  <div class="aspect-w-16 aspect-h-3 relative bg-black">
    <img
      class="object-cover h-full w-full absolute"
      src="https://picsum.photos/1200/600"
      alt="Cover photo">
  </div>
  <div class="-mt-6 container flex items-center">
    <div class="avatar rounded-full p-1 bg-white">
      <div class="w-32 h-32 rounded-full">
        <img src="https://picsum.photos/100/100">
      </div>
    </div>
    <div class="ml-3">
      <div class="text-2xl font-bold">{{ user.username }}</div>
      <div class="flex items-center">
        <icon-heart
          class="mr-2 fill-current text-error"
          :size="16"></icon-heart>
        136 followers
      </div>
    </div>
  </div>
  <div class="container">
    <div class="row">
      <div class="tabs mt-6">
        <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.HOME }" @click="activeTab = tabName.HOME;">Home</div>
        <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.TIERS }" @click="activeTab = tabName.TIERS;">Membership Tiers</div>
        <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.POSTS }" @click="activeTab = tabName.POSTS;">Posts</div>
        <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.DONATIONS }" @click="activeTab = tabName.DONATIONS;">Donations</div>
        <div class="tab tab-lg tab-lifted flex-grow cursor-default"></div>
      </div>
    </div>
    <div v-if="activeTab == tabName.TIERS" class="row">
      <tier
        v-for="tier in user.tiers"
        :key="tier.id"
        :user="user"
        :tier="tier"></tier>
    </div>
  </div>
</div>
</template>

<script>
import tier from '../components/tier.vue';
export default {
  components: { tier },
  layout: 'default-no-container',
  props: {
    username: {
      type: String,
      default: null
    }
  },
  data() {
    const tabName = {
      HOME: 'home',
      TIERS: 'tiers',
      POSTS: 'posts',
      DONATIONS: 'donations'
    };
    return {
      user: null,
      tabName,
      activeTab: tabName.TIERS
    };
  },
  async fetch() {
    const username = this.username || this.$auth.user.username;
    this.user = await this.$axios.$get(`/api/users/${username}/`);
  }
};
</script>

<style>
</style>
