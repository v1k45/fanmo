<template>
<profile-feed
  v-if="sectionsLoaded && user"
  :loading="loading"
  :posts-loading="postsLoading"
  :is-preview-mode="isPreviewMode"
  :loading-locked-post-id="loadingLockedPostId"
  v-on="$listeners">
</profile-feed>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
export default {
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    postsLoading: {
      type: Boolean,
      default: false
    },
    isPreviewMode: {
      type: Boolean,
      default: false
    },
    loadingLockedPostId: {
      type: Number,
      default: null
    }
  },
  computed: {
    ...mapGetters('posts', ['sectionsLoaded']),
    ...mapState('profile', ['user'])
  }
};
</script>

