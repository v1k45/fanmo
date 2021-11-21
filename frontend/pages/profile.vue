<template>
<div v-if="user != null">
  <div class="aspect-w-16 aspect-h-3 relative bg-black">
    <img
      class="object-cover h-full w-full absolute"
      :src="user.cover.big"
      alt="Cover photo">
  </div>
  <div class="-mt-6 container flex items-center">
    <div class="avatar rounded-full p-1 bg-white">
      <div class="w-32 h-32 rounded-full">
        <img :src="user.avatar.medium">
      </div>
    </div>
    <div class="ml-3">
      <div class="text-2xl font-bold">{{ user.name || user.username }}</div>
      <div class="flex items-center">
        <icon-heart
          class="mr-2 fill-current text-error"
          :size="16"></icon-heart>
        {{ user.follower_count }} followers
      </div>
    </div>
    <button class="btn btn-black ml-auto" @click="toggleFollow">
      {{ user.is_following ? 'Unfollow' : 'Follow' }}
    </button>
  </div>
  <div class="container">
    <div class="my-6">
      <div class="tabs">
        <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.HOME }" @click="activeTab = tabName.HOME;">Home</div>
        <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.TIERS }" @click="activeTab = tabName.TIERS;">Membership Tiers</div>
        <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.POSTS }" @click="activeTab = tabName.POSTS;">Posts</div>
        <div class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.DONATIONS }" @click="activeTab = tabName.DONATIONS;">Donations</div>
        <div class="tab tab-lg tab-lifted flex-grow cursor-default"></div>
      </div>
    </div>
    <div v-show="activeTab == tabName.TIERS" class="row justify-center pb-10">
      <tier
        v-for="tier in user.tiers"
        :key="tier.id"
        :user="user"
        :tier="tier"></tier>
    </div>
    <div v-show="activeTab == tabName.POSTS" class="pb-10">
      <div class="max-w-3xl mx-auto">
        <div class="flex flex-wrap">
          <h1 class="text-2xl font-bold mr-auto">Posts</h1>
          <button class="mt-4 sm:mt-0 btn btn-wide btn-black" @click="isAddPostVisible = true;">
            <IconPlus class="mr-1" :size="16"></IconPlus>
            Add a post
          </button>
        </div>
        <div v-if="posts.count" class="mt-8">
          <post v-for="post in posts.results" :key="post.id" :post="post" class="mb-6"></post>
        </div>
      </div>
    </div>
    <add-post v-model="isAddPostVisible"></add-post>
    <div v-show="activeTab == tabName.DONATIONS" class="row justify-end pb-10">
      <div v-if="donations.count" class="col-12 md:col-6">
        <div class="row justify-center">
          <donation v-for="donation in donations.results" :key="donation.id" :donation="donation">
          </donation>
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="row justify-center">
          <donation-form :user="user"></donation-form>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import AddPost from '../components/add-post.vue';
import DonationForm from '../components/donation-form.vue';
import donation from '../components/donation.vue';
import post from '../components/post.vue';
import tier from '../components/tier.vue';
export default {
  components: { tier, DonationForm, donation, post, AddPost },
  layout:
    'default-no-container',
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
      donations: {},
      posts: {},
      user: null,
      tabName,
      activeTab: tabName.TIERS,
      isAddPostVisible: false
    };
  },
  async fetch() {
    const username = this.username || this.$auth.user.username;
    this.user = await this.$axios.$get(`/api/users/${username}/`);
    this.donations = await this.$axios.$get(`/api/donations/?username=${username}`);
    this.posts = await this.$axios.$get(`/api/posts/?username=${username}`);
  },
  head: {
    title: 'My profile'
  },
  methods: {
    async toggleFollow() {
      const action = this.user.is_following ? 'unfollow' : 'follow';
      this.user = await this.$axios.$post(`/api/users/${this.user.username}/${action}/`);
    }
  }
};
</script>
