<template>
<div v-loading="loading" class="bg-gray-50 flex-grow min-h-screen">
  <!-- sticky header start -->
  <header v-if="user" class="bg-white sticky z-20 top-0 w-full border-b">
    <div class="lg:container px-4 lg:px-0 flex items-center py-2">

      <breakpoint-helper></breakpoint-helper>

      <nuxt-link :to="`/${user.username}/`" class="flex flex-grow items-center mr-auto max-w-[65%] md:max-w-[55%]">
        <fm-avatar :src="user.avatar && user.avatar.medium" :name="user.display_name" size="w-8 h-8 lg:w-10 lg:h-10" class="flex-shrink-0"></fm-avatar>

        <div class="ml-2 lg:ml-3 max-w-full">
          <div v-tooltip="user.display_name" class="text-base lg:text-lg text-black font-bold leading-none lg:leading-none max-w-max truncate">{{ user.display_name }}</div>
          <div v-if="user.one_liner" v-tooltip="user.one_liner" class="mt-1 text-xs lg:text-sm text-gray-500 max-w-max truncate">{{ user.one_liner }}</div>
        </div>
      </nuxt-link>

      <fm-input v-model="activeTab" type="select" size="sm" class="mx-4 hidden md:block" @change="gotoTab()">
        <option :value="null" disabled selected>Jump to</option>
        <option :value="tabName.POSTS">Feed</option>
        <option v-if="shouldShowTiersTab" :value="tabName.TIERS">Memberships</option>
        <option :value="tabName.DONATION">Tip</option>
      </fm-input>

      <fm-button :type="user.is_following ? 'success' : 'primary'" class="w-36 hidden md:block" :loading="isFollowLoading" @click="toggleFollow">
        <div v-if="user.is_following" class="flex items-center justify-center">
          <icon-check class="inline-block mr-1 h-em w-em flex-shrink-0"></icon-check> Following
        </div>
        <div v-else class="flex items-center justify-center">
          <icon-plus class="inline-block mr-1 h-em w-em flex-shrink-0"></icon-plus> Follow
        </div>
      </fm-button>

      <layout-navigation
        :type="$auth.loggedIn ? 'hamburger-minimal' : 'anonymous-hamburger'"
        class="rounded-full ml-4">
      </layout-navigation>
    </div>

  </header>
  <!-- sticky header end -->

  <div class="container py-8">
    <div v-if="postDeleted" class="max-w-md mt-[20vh] mx-auto">
      <fm-alert type="error" :show-icon="false">This post has been deleted.</fm-alert>
      <div class="flex mt-4">
        <fm-button block class="mr-2" @click="$router.replace('/auth')">Dashboard</fm-button>
        <fm-button type="primary" block class="ml-2" @click="$router.replace(`/${$auth.user.username}`)">Go to your profile</fm-button>
      </div>
    </div>
    <div v-else class="max-w-6xl grid grid-cols-12 gap-5 mx-auto">
      <div class="col-span-12 lg:col-span-7">
        <!-- TODO: showCreatorInfo on phone [needs breakpoint service] -->
        <profile-post
          v-if="post"
          :post="post"
          @share-click="sharePost.isVisible = true;" @deleted="handleDeleted">
          <template #bottom>
            <hr>
            <comments class="post-body mb-4" v-bind="{ post }">
              <template #locked>
                <div v-if="post.minimum_tier" class="mt-4">
                  <div class="py-4 bg-gray-100 text-center rounded-xl">
                    <fm-button
                      type="" class="text-body" @click="handleSubscribeIntent">
                      Join now for {{ $currency(post.minimum_tier.amount) }}/month to comment
                    </fm-button>
                  </div>
                </div>
              </template>
            </comments>
          </template>
        </profile-post>
      </div>
      <div v-if="user" class="col-span-12 lg:col-span-5 h-full">
        <div class="lg:hidden mt-4"></div>

        <fm-card class="overflow-hidden sticky top-20">
          <div class="text-xl text-black font-bold truncate mb-3">About</div>

          <fm-read-more lines="2" class="lg:hidden mb-4">
            <fm-markdown-styled>
              <div v-html="user.about"></div>
            </fm-markdown-styled>
          </fm-read-more>
          <fm-read-more lines="6" class="hidden lg:block mb-4">
            <fm-markdown-styled>
              <div v-html="user.about"></div>
            </fm-markdown-styled>
          </fm-read-more>

          <div v-if="user && user.social_links" class="flex justify-center space-x-4 text-gray-600">
            <a v-if="user.social_links.website_url" class="unstyled hover:text-gray-800" title="Website" target="_blank" :href="user.social_links.website_url">
              <icon-globe :size="24"></icon-globe>
            </a>
            <a v-if="user.social_links.twitter_url" class="unstyled hover:text-gray-800" title="Twitter" target="_blank" :href="user.social_links.twitter_url">
              <icon-twitter :size="24"></icon-twitter>
            </a>
            <a v-if="user.social_links.youtube_url" class="unstyled hover:text-gray-800" title="Youtube" target="_blank" :href="user.social_links.youtube_url">
              <icon-youtube :size="24"></icon-youtube>
            </a>
            <a v-if="user.social_links.instagram_url" class="unstyled hover:text-gray-800" title="Instagram" target="_blank" :href="user.social_links.instagram_url">
              <icon-instagram :size="24"></icon-instagram>
            </a>
            <a v-if="user.social_links.facebook_url" class="unstyled hover:text-gray-800" title="Facebook" target="_blank" :href="user.social_links.facebook_url">
              <icon-facebook :size="24"></icon-facebook>
            </a>
          </div>
        </fm-card>
      </div>
    </div>
  </div>

  <!-- footer start -->
  <footer class="mt-auto pt-4 pb-20 md:pb-4 px-6 text-center">
    <div class="text-sm ml-7">Powered by</div>
    <nuxt-link to="/" class="mx-auto inline-block">
      <logo class="h-6"></logo>
    </nuxt-link>
  </footer>
  <!-- footer end -->

  <!-- phone bottom pane tab nav start -->
  <nav class="bottom-0 fixed z-20 w-full bg-white border-t md:hidden py-1 shadow">
    <ul class="flex items-center h-full max-w-full sm:max-w-md md:max-w-lg mx-2 sm:mx-auto justify-around">
      <li class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <div
          class="unstyled rounded-xl focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          :class="{ 'text-white bg-fm-primary pointer-events-none': activeTab === tabName.POSTS }"
          @click="gotoTab(tabName.POSTS)">

          <icon-image class="h-6 w-6"></icon-image>
          <div class="mt-1 truncate" title="Feed">Feed</div>
        </div>
      </li>
      <li v-if="shouldShowTiersTab" class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <div
          class="unstyled rounded-xl focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          :class="{ 'text-white bg-fm-primary pointer-events-none': activeTab === tabName.TIERS }"
          @click="gotoTab(tabName.TIERS)">

          <icon-crown class="h-6 w-6"></icon-crown>
          <div class="mt-1 truncate" title="Feed">Memberships</div>
        </div>
      </li>
      <li class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <div
          class="unstyled rounded-xl focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          :class="{ 'text-white bg-fm-primary pointer-events-none': activeTab === tabName.DONATION }"
          @click="gotoTab(tabName.DONATION)">

          <icon-coins class="h-6 w-6"></icon-coins>
          <div class="mt-1 truncate" title="Feed">Tips</div>
        </div>
      </li>
    </ul>
  </nav>
  <!-- phone bottom pane tab nav end -->

  <profile-share
    v-if="post"
    v-model="sharePost.isVisible"
    :text="post.title"
    :relative-url="`/p/${post.slug}/${post.id}/`">
  </profile-share>
</div>
</template>

<script>
import cloneDeep from 'lodash/cloneDeep';
import { mapActions, mapGetters, mapMutations } from 'vuex';
import get from 'lodash/get';
export default {
  layout: 'empty',
  auth: false,
  data() {
    const tabName = {
      POSTS: 'posts',
      TIERS: 'tiers',
      DONATION: 'donation'
    };
    return {
      tabName,
      activeTab: null,
      postDeleted: false,
      loading: false,
      deletedCopy: null, // to be used after deletion
      sharePost: {
        isVisible: false
      },
      isFollowLoading: false
    };
  },
  async fetch() {
    this.loading = true;
    await Promise.allSettled([
      this.loadPost(this.$route.params.id)
    ]);
    this.loading = false;
  },
  head() {
    return {
      title: this.post ? `${this.post.title} - ${this.post.author_user.display_name}` : ''
    };
  },
  computed: {
    ...mapGetters('posts', ['currentPost', 'isDeleted']),

    post() {
      return this.currentPost || this.deletedCopy;
    },
    user() {
      return this.currentPost ? this.currentPost.author_user : null;
    },
    url() {
      return location.href;
    },
    isSelfProfile() {
      return !!(
        (get(this.$auth, 'user.username') && this.post.author_user.username) &&
        (this.$auth.user.username === this.post.author_user.username)
      );
    },
    shouldShowTiersTab() {
      if (!this.user) return false;
      const hasTiers = !!this.user.tiers.length;
      return this.isSelfProfile || hasTiers;
    }
  },
  watch: {
    currentPost: {
      immediate: true,
      handler(post) {
        if (!post) return;
        this.deletedCopy = cloneDeep(post);
      }
    }
  },
  created() {
    if (this.$route.params.share === '1') {
      this.sharePost.isVisible = true;
    }
  },
  beforeDestroy() {
    this.unsetCurrentPost();
  },
  methods: {
    ...mapActions('posts', ['loadPost']),
    ...mapActions('profile', ['follow', 'unfollow']),
    ...mapMutations('posts', ['unsetCurrentPost', 'updatePostUser']),
    ...mapMutations('ui', ['setGlobalLoader']),

    handleDeleted() {
      this.postDeleted = true;
    },
    async toggleFollow() {
      // TODO: redirect back to this after login and dispatch follow automatically
      if (!this.$auth.loggedIn) return this.$router.push('/login');
      this.isFollowLoading = true;
      const { data: user } = await (this.user.is_following ? this.unfollow(this.user.username) : this.follow(this.user.username));
      this.updatePostUser({ postId: this.post.id, user });
      this.isFollowLoading = false;
    },
    gotoTab(tabName) {
      this.$router.push({
        name: 'username',
        params: {
          username: this.post.author_user.username,
          data: {
            intent: 'preselect-tab',
            tab: tabName || this.activeTab
          }
        }
      });
    },
    handleSubscribeIntent() {
      this.setGlobalLoader('Just a moment...');
      this.$router.push({
        name: 'username',
        params: {
          username: this.post.author_user.username,
          data: {
            intent: 'subscribe-through-post',
            tier: this.post.minimum_tier
          }
        }
      });
    }
  }
};
</script>
