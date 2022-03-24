<template>
<div v-if="user != null">
  <div class="aspect-w-16 aspect-h-3 relative bg-black">
    <img
      class="object-cover h-full w-full absolute"
      v-if="user.cover"
      :src="user.cover.big"
      alt="Cover photo">
  </div>
  <div class="-mt-6 container flex items-center">
    <div class="avatar rounded-full p-1 bg-white">
      <div class="w-32 h-32 rounded-full">
        <img v-if="user.avatar" :src="user.avatar.medium">
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
        <div v-if="user.tiers.length" class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.TIERS }" @click="activeTab = tabName.TIERS;">Membership Tiers</div>
        <div v-if="user.preferences.is_accepting_payments" class="tab tab-lg tab-lifted" :class="{ 'tab-active': activeTab === tabName.DONATIONS }" @click="activeTab = tabName.DONATIONS;">Donations</div>
        <div class="tab tab-lg tab-lifted flex-grow cursor-default"></div>
      </div>
    </div>
    <div v-show="activeTab == tabName.HOME" class="row pb-10">
      <div class="col-7">
        <div class="flex flex-wrap items-center">
          <h1 class="text-2xl font-bold mr-auto">Posts</h1>
          <button v-if="$auth.loggedIn && user.username == $auth.user.username" class="mt-4 sm:mt-0 btn btn-wide btn-black" @click="isAddPostVisible = true;">
            <IconPlus class="mr-1" :size="16"></IconPlus>
            Add a post
          </button>
        </div>
        <div v-if="posts.count" class="mt-8 max-w-lg">
          <post v-for="post in posts.results" :key="post.id" :post="post" class="mb-6"></post>
        </div>
      </div>
      <div class="col"></div>
      <div class="col-4">
        <h1 class="text-2xl font-bold mr-auto">About</h1>
        <div class="card shadow my-8">
          <div class="card-body">
            <p>{{ user.about || 'Nothing to see here' }}</p>
            <div class="card-actions">
              <a v-if="user.social_links.website_url" :href="user.social_links.website_url">
                <icon-globe class="mr-1" :size="20"></icon-globe>
              </a>
              <a v-if="user.social_links.youtube_url" :href="user.social_links.youtube_url">
                <icon-youtube class="mr-1" :size="20"></icon-youtube>
              </a>
              <a v-if="user.social_links.facebook_url" :href="user.social_links.facebook_url">
                <icon-facebook class="mr-1" :size="20"></icon-facebook>
              </a>
              <a v-if="user.social_links.instagram_url" :href="user.social_links.instagram_url">
                <icon-instagram class="mr-1" :size="20"></icon-instagram>
              </a>
              <a v-if="user.social_links.twitter_url" :href="user.social_links.twitter_url">
                <icon-twitter class="mr-1" :size="20"></icon-twitter>
              </a>
            </div>
          </div>
        </div>
        <h1 class="text-2xl font-bold mr-auto">Recent Donations</h1>
        <div class="row">
          <donation v-for="donation in donations.results" :key="donation.id" :donation="donation">
          </donation>
        </div>
      </div>
    </div>
    <add-post v-model="isAddPostVisible" @created="prependPost"></add-post>
    <div v-show="activeTab == tabName.TIERS" class="row justify-center pb-10">
      <tier
        v-for="tier in user.tiers"
        :key="tier.id"
        :user="user"
        :tier="tier"></tier>
    </div>
    <div v-show="activeTab == tabName.DONATIONS" class="row justify-end pb-10">
      <div v-if="donations.count" class="col-12 md:col-6">
        <div class="row justify-center">
          <donation v-for="donation in donations.results" :key="donation.id" :donation="donation">
          </donation>
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="row justify-center">
          <donation-form :user="user" @donated="prependDonation"></donation-form>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
export default {
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
      DONATIONS: 'donations'
    };
    return {
      donations: {},
      posts: {},
      user: null,
      tabName,
      activeTab: tabName.HOME,
      isAddPostVisible: false
    };
  },
  async fetch() {
    const username = this.username || this.$auth.user.username;
    this.user = await this.$axios.$get(`/api/users/${username}/`);
    this.posts = await this.$axios.$get(`/api/posts/?username=${username}`);
    this.donations = await this.$axios.$get(`/api/donations/?username=${username}`);
  },
  head: {
    title: 'My profile'
  },
  methods: {
    async toggleFollow() {
      const action = this.user.is_following ? 'unfollow' : 'follow';
      this.user = await this.$axios.$post(`/api/users/${this.user.username}/${action}/`);
    },
    prependPost(post) {
      this.posts.results.unshift(post);
    },
    prependDonation(donation) {
      this.donations.results.unshift(donation);
    }
  }
};
</script>
