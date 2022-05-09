<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <div class="container sm:pl-0 pb-16  rounded-xl">
    <div class="row xl:gx-5">
      <!-- posts start -->
      <div class="col-12 md:col-auto md:max-w-2xl md:flex-grow lg:col-8 lg:max-w-none lg:flex-grow-0 xl:col-auto xl:max-w-2xl xl:flex-grow mx-auto">
        <div class="text-2xl text-black font-bold">Posts</div>
        <div class="mt-1 text-gray-600 mb-5">Posts from all the creators you follow or subscribe to.</div>
        <template v-if="feedPosts">
          <profile-post
            v-for="post in feedPosts.results" :key="post.id" :post="post"
            class="mb-6 md:mb-8" show-creator-info @share-click="handleShareClick">
          </profile-post>
        </template>
        <div v-if="feedPosts && feedPosts.next" class="text-center mt-4">
          <fm-button :loading="nextPostsLoading" @click="loadNextPostsLocal">Load more</fm-button>
        </div>
        <div v-if="feedPosts && !feedPosts.results.length" class="text-sm text-gray-500">
          No posts to show here yet.
        </div>
      </div>
      <!-- posts end -->

      <!-- following users start -->
      <div class="hidden lg:block col-12 lg:col overflow-hidden">
        <div class="text-xl text-black font-bold">Following <template v-if="following.results.length">({{ following.results.length }})</template></div>
        <div class="mt-1 text-gray-600 mb-5">Creators you follow.</div>

        <template v-if="following">
          <nuxt-link
            v-for="(user, idx) in following.results" :key="user.id" :to="`/${user.username}`"
            class="flex items-center border-l border-t border-r bg-white px-4 py-3 hover:bg-gray-200" :class="{
              'rounded-t-xl': idx === 0,
              'rounded-b-xl border-b': idx === following.results.length - 1
            }">
            <fm-avatar
              :src="user.avatar && user.avatar.small"
              :name="user.display_name" :username="user.username"
              size="w-8 h-8 mr-2 inline-block flex-shrink-0">
            </fm-avatar>
            <div class="overflow-hidden">
              <div class="truncate text-base text-black font-medium" :title="user.display_name">{{ user.display_name }}</div>
              <div v-if="user.one_liner" :title="user.one_liner" class="truncate text-sm text-gray-500">{{ user.one_liner }}</div>
            </div>
          </nuxt-link>
        </template>
        <div v-if="following.next" class="text-center mt-4">
          <fm-button size="sm" :loading="nextFollowingUsersLoading" @click="loadNextFollowingUsersLocal">Load more</fm-button>
        </div>
        <div v-if="following && !following.results.length" class="text-sm text-gray-500">
          You aren't following anyone yet.
        </div>
      </div>
      <!-- following users end -->
    </div>
  </div>

  <!-- following phone dialog start -->
  <div v-if="following.results" class="fixed top-1/2 transform -translate-y-1/2 right-0 lg:hidden">
    <button
      class="py-4 px-2 border border-r-0 bg-white rounded-l-xl text-center hover:bg-fm-primary-100 hover:text-fm-primary"
      @click="isFollowingDialogVisible = true;">
      <span class="[writing-mode:vertical-rl] [text-orientation:mixed] font-medium text-sm">
        Following <template v-if="following.results.length">({{ following.results.length }})</template>
      </span>
    </button>
  </div>

  <fm-dialog v-model="isFollowingDialogVisible" drawer no-padding>
    <template #header>
      <div class="text-base">
        Following <template v-if="following.results.length">({{ following.results.length }})</template>
      </div>
    </template>
    <template v-if="isFollowingDialogVisible && following">
      <nuxt-link
        v-for="(user) in following.results" :key="user.id" :to="`/${user.username}`"
        class="flex items-center border-l border-b border-r bg-white px-4 py-3 hover:bg-gray-200">
        <fm-avatar
          :src="user.avatar && user.avatar.small"
          :name="user.display_name" :username="user.username"
          size="w-8 h-8 mr-2 inline-block flex-shrink-0">
        </fm-avatar>
        <div class="overflow-hidden">
          <div class="truncate text-base text-black font-medium" :title="user.display_name">{{ user.display_name }}</div>
          <div v-if="user.one_liner" :title="user.one_liner" class="truncate text-sm text-gray-500">{{ user.one_liner }}</div>
        </div>
      </nuxt-link>
      <div v-if="following.next" class="text-center mt-4">
        <fm-button size="sm" :loading="nextFollowingUsersLoading" @click="loadNextFollowingUsersLocal">Load more</fm-button>
      </div>
    </template>
    <div v-if="following && !following.results.length" class="text-sm text-gray-500 p-6 text-center">
      You aren't following anyone yet.
    </div>
  </fm-dialog>
  <!-- following phone dialog end -->

  <!-- dialogs start -->
  <profile-share v-model="sharePost.isVisible" :text="sharePost.text" :url="sharePost.url"></profile-share>
  <!-- dialogs end -->
</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
export default {
  auth: true,
  layout: 'with-sidebar',
  data() {
    return {
      nextPostsLoading: false,
      nextFollowingUsersLoading: false,
      isFollowingDialogVisible: false,
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
    ...mapGetters('posts', ['feedPosts']),
    ...mapGetters('users', ['following'])
  },
  mounted() {
    this.loadFeedPosts();
    this.loadFollowingUsers();
  },
  methods: {
    ...mapActions('posts', ['loadFeedPosts', 'loadNextFeedPosts']),
    ...mapActions('users', ['loadFollowingUsers', 'loadNextFollowingUsers']),
    async loadNextPostsLocal() {
      this.nextPostsLoading = true;
      await this.loadNextFeedPosts();
      this.nextPostsLoading = false;
    },
    async loadNextFollowingUsersLocal() {
      this.nextFollowingUsersLoading = true;
      await this.loadNextFollowingUsers();
      this.nextFollowingUsersLoading = false;
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
