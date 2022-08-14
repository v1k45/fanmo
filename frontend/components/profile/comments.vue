<template>
<div>
  <fm-form v-if="post.can_comment" class="mt-4 pt-4 border-t-2 post-body" :errors="commentErrors" @submit.prevent="createCommentLocal">
    <div class="flex">
      <fm-avatar
        :src="$auth.user.avatar && $auth.user.avatar.small"
        :name="$auth.user.display_name"
        size="w-12 h-12 flex-shrink-0 mr-6">
      </fm-avatar>
      <fm-input
        v-model="commentForm.body" uid="body" type="textarea" class="flex-grow"
        rows="2" placeholder="Leave a comment" @focus="isCommentBoxFocused = true;" @blur="isCommentBoxFocused = false;"></fm-input>
    </div>
    <div v-if="commentForm.body || isCommentBoxFocused" class="text-right mt-3">
      <fm-button type="primary" native-type="submit">Comment</fm-button>
    </div>
  </fm-form>
  <div v-else class="post-body mt-4 mb-8">
    <div class="py-4 bg-gray-100 text-center rounded-xl">
      <fm-button
        type="" class="text-body" @click="handleSubscribeIntent">
        Join now for {{ $currency(post.minimum_tier.amount) }}/month to comment
      </fm-button>
    </div>
  </div>

  <div class="mt-4 post-body">
    <profile-comment
      v-for="comment in (comments || [])"
      :key="comment.id" :comment="comment" :post="post" class="mt-6">
    </profile-comment>

    <div v-if="post.hasMoreComments" class="text-center my-6">
      <fm-button type="link" :loading="nextCommentsLoading" @click="loadNextCommentsLocal">Load more comments</fm-button>
    </div>
  </div>
</div>
</template>

<script>
import { mapActions, mapMutations } from 'vuex';
export default {
  props: {
    post: { type: Object, default: null },
    comments: { type: Array, default: null }
  },
  data() {
    return {
      isCommentBoxFocused: false,
      nextCommentsLoading: false,
      commentErrors: {},
      commentForm: {
        body: ''
      }
    };
  },
  methods: {
    ...mapActions('posts', ['createComment', 'loadNextComments']),
    ...mapMutations('ui', ['setGlobalLoader']),

    async createCommentLocal() {
      const { success, data } = await this.createComment({ postId: this.post.id, body: this.commentForm.body });
      if (!success) this.commentErrors = data;
      else {
        this.commentForm.body = '';
        this.commentErrors = {};
      }
    },
    async loadNextCommentsLocal() {
      this.nextCommentsLoading = true;
      await this.loadNextComments(this.post.id);
      this.nextCommentsLoading = false;
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

<style>

</style>
