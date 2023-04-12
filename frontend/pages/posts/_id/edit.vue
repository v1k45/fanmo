<template>
<div v-loading="loading">
  <profile-edit-post v-if="post && isSelfProfile" v-model="visible" :post="post"></profile-edit-post>
  <fm-card
    v-else
    class="mx-auto max-w-xl overflow-hidden" body-class="text-center !pt-16 !pb-20">
    <icon-server-crash class="h-16 w-16 stroke-1 animatecss animatecss-spin"></icon-server-crash>
    <div class="mt-2 font-medium">
      Looks like there was an error finding this post.
    </div>
    <div class="mt-2">
      The post you are trying to edit either does not exist or you don't have appropriate permission to access it.
    </div>
  </fm-card>
</div>
</template>

<script>
import get from 'lodash/get';
import { mapActions, mapGetters } from 'vuex';

export default {
  data() {
    return {
      loading: true,
      visible: true
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
    ...mapGetters('posts', ['currentPost']),

    post() {
      return this.currentPost;
    },
    user() {
      return this.currentPost ? this.currentPost.author_user : null;
    },
    url() {
      return location.href;
    },
    isSelfProfile() {
      return !!(
        (get(this.$auth, 'user.username') && get(this.post, 'author_user.username')) &&
        (this.$auth.user.username === this.post.author_user.username)
      );
    }
  },
  watch: {
    visible(val) {
      if (!val) {
        this.$router.push({ name: 'p-slug-id', params: { slug: this.post.slug, id: this.post.id } });
      }
    }
  },
  methods: {
    ...mapActions('posts', ['loadPost'])
  }
};
</script>

<style></style>
