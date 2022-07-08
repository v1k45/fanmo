<template>
<div class="bg-gray-50 py-8 flex-grow">
  <div class="container">
    <div v-if="postDeleted" class="max-w-md mt-[20vh] mx-auto">
      <fm-alert type="error" :show-icon="false">This post has been deleted.</fm-alert>
      <div class="flex mt-4">
        <!-- TODO: wire to correct dashboard link -->
        <fm-button block class="mr-2" @click="$router.replace('/dashboard')">Dashboard</fm-button>
        <fm-button type="primary" block class="ml-2" @click="$router.replace('/profile')">Go to your profile</fm-button>
      </div>
    </div>
    <div v-else class="max-w-6xl grid grid-cols-12 gap-5 mx-auto">
      <div class="col-span-12 lg:col-span-7">
        <!-- TODO: showCreatorInfo on phone [needs breakpoint service] -->
        <profile-post v-if="post" :post="post" @share-click="sharePost.isVisible = true;" @deleted="handleDeleted">
          <template #bottom>
            <profile-comments v-bind="{ post, comments }"></profile-comments>
          </template>
        </profile-post>
      </div>
      <div v-if="user" class="col-span-12 lg:col-span-5 h-full">
        <div class="lg:hidden">
          <hr class="my-4">
          <div class="text-lg font-bold mb-4">
            About the creator
          </div>
        </div>
        <fm-card class="overflow-hidden sticky top-20">

          <nuxt-link class="flex flex-wrap items-center" :to="`/${user.username}/`">
            <!-- avatar start -->
            <fm-avatar
              :src="user.avatar && user.avatar.medium"
              :name="user.name" :username="user.username"
              size="w-16 h-16 flex-shrink-0">
            </fm-avatar>
            <!-- avatar end -->

            <!-- author name and one liner start -->
            <div class="ml-3 min-w-0 text-body">
              <div class="font-bold text-lg truncate" :title="user.name || user.username">
                {{ user.name || user.username }}
              </div>
              <div v-if="user.one_liner" class="text-gray-500">{{ user.one_liner }}</div>
            </div>
            <!-- author name and one liner end -->
          </nuxt-link>

          <hr class="my-4">

          <fm-read-more v-if="user && user.about" lines="6" class="mb-4">
            <p v-html="user.about"></p>
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

  <profile-share
    v-if="post"
    v-model="sharePost.isVisible"
    :text="post.title"
    :relative-url="post.slug">
  </profile-share>
</div>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex';
export default {
  layout: 'default-no-container',
  auth: false,
  data() {
    return {
      postDeleted: false,
      sharePost: {
        isVisible: false
      }
    };
  },
  async fetch() {
    await Promise.allSettled([
      this.loadPost(this.$route.params.id),
      this.loadComments(this.$route.params.id)
    ]);
  },
  computed: {
    ...mapGetters('posts', ['currentPost', 'isDeleted']),

    post() {
      return this.currentPost;
    },
    user() {
      return this.currentPost ? this.currentPost.author_user : null;
    },
    comments() {
      return this.currentPost ? this.currentPost.comments : null;
    },
    url() {
      return location.href;
    }
  },
  beforeDestroy() {
    this.unsetCurrentPost();
  },
  methods: {
    ...mapActions('posts', ['loadPost', 'loadComments']),
    ...mapMutations('posts', ['unsetCurrentPost']),
    handleDeleted() {
      this.postDeleted = true;
    }
  }
};
</script>
