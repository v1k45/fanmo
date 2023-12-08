<template>
<div class="container">
  <fm-card v-if="user.about || isSelfProfile" class="max-w-3xl mx-auto">
    <div v-if="user.about" class="my-4">
      <fm-markdown-styled>
        <div v-html="user.about"></div>
      </fm-markdown-styled>
    </div>
    <div
      v-else
      class="mx-auto overflow-hidden text-center pt-10 pb-14">
      <icon-scroll class="h-16 w-16 stroke-1"></icon-scroll>
      <div class="mt-2">
        Start by telling your fans a bit about yourself and where they can find you.

        <div class="text-sm text-gray-500 mt-3">
          Click on <span class="text-black">Edit Page</span> to get started.
        </div>

      </div>
    </div>
    <div class="flex justify-center space-x-4 text-gray-600">
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
    <div class="flex items-center justify-center space-x-3 border-t mt-4 py-4">
      <fm-button type="primary">
        <icon-crown class="h-em w-em"></icon-crown> Join
      </fm-button>
      <fm-button type="primary">
        <icon-coins class="h-em w-em"></icon-coins> Tip
      </fm-button>
    </div>
  </fm-card>
</div>
</template>

<script>
import { mapState } from 'vuex';
export default {
  computed: {
    ...mapState('profile', ['user'])
  }
};
</script>
