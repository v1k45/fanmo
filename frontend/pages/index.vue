<template>
<div>
  <div v-if="false" class="row row-cols-5 g-4">
    <div>
      <nuxt-link to="/" class="flex flex-col border items-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <IconHome :size="36"></IconHome>
        <div class="mt-2">Home</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/profile" class="flex flex-col border items-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-layout :size="36"></icon-layout>
        <div class="mt-2">Profile</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/subscriptions" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-user-plus :size="36"></icon-user-plus>
        <div class="mt-2">Subscriptions</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/subscribers" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-users :size="36"></icon-users>
        <div class="mt-2">Subscribers</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/payments" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-wallet :size="36"></icon-wallet>
        <div class="mt-2">Payments</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/payouts" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-indian-rupee :size="36"></icon-indian-rupee>
        <div class="mt-2">Payouts</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/tiers" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <IconListMinus :size="36"></IconListMinus>
        <div class="mt-2">Manage tiers</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/settings" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-settings :size="36"></icon-settings>
        <div class="mt-2">Settings</div>
      </nuxt-link>
    </div>
  </div>

  <div v-if="false" class="text-center pt-16">
    <div class="mb-6">
      Sign up by clicking on the button below to get started!
    </div>
    <nuxt-link to="/register" class="btn px-10 animate-bounce">Sign up</nuxt-link>
  </div>

  <h1 class="text-2xl font-bold my-4">Featured Creators</h1>
  <div class="row row-cols-5 g-4">
    <div v-for="user in creators.results" :key="user.id">
      <nuxt-link :to="`/${user.username}`" class="flex flex-col border items-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <fm-avatar
          :src="user.avatar && user.avatar.medium"
          :name="user.name" :username="user.username"
          size="h-24 w-24">
        </fm-avatar>
        <div class="mt-2">{{ user.username }}</div>
      </nuxt-link>
    </div>
  </div>

  <h1 class="text-2xl font-bold my-8">Posts</h1>
  <div v-if="feedPosts.results.length" class="mt-8 max-w-lg">
    <profile-post
      v-for="post in feedPosts.results" :key="post.id" :post="post"
      class="mb-6 md:mb-8" @share-click="handleShareClick"></profile-post>
  </div>
  <div v-if="feedPosts.next" class="text-center mt-4">
    <fm-button :loading="nextPostsLoading" @click="loadNextPostsLocal">Load more</fm-button>
  </div>
  <profile-share v-model="sharePost.isVisible" :text="sharePost.text" :url="sharePost.url"></profile-share>
</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
export default {
  auth: false,
  layout: 'with-sidebar',
  async asyncData({ $axios }) {
    const creators = await $axios.$get('/api/users/?is_creator=true');
    return { creators };
  },
  data() {
    return {
      nextPostsLoading: false,
      sharePost: {
        isVisible: false,
        url: null,
        text: null
      }
    };
  },
  head: {
    title: 'Home'
  },
  computed: {
    ...mapGetters('posts', ['feedPosts'])
  },
  mounted() {
    this.loadFeedPosts();
  },
  methods: {
    ...mapActions('posts', ['loadFeedPosts', 'loadNextFeedPosts']),
    async loadNextPostsLocal() {
      this.nextPostsLoading = true;
      await this.loadNextFeedPosts();
      this.nextPostsLoading = false;
    },
    handleShareClick(post) {
      this.sharePost = {
        isVisible: true,
        url: post.slug,
        text: post.title
      };
    }
  }
};
</script>
