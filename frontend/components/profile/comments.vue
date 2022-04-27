<template>
<div>
  <fm-form v-if="post.can_comment" class="mt-4 pt-4 border-t-2 post-body" :errors="commentErrors" @submit.prevent="createCommentLocal">
    <div class="flex">
      <fm-avatar
        v-if="$auth.loggedIn"
        :src="$auth.user.avatar && $auth.user.avatar.small"
        :name="$auth.user.name" :username="$auth.user.username"
        size="w-12 h-12 flex-shrink-0 mr-6">
      </fm-avatar>
      <fm-avatar v-else size="w-12 h-12 flex-shrink-0 mr-6"></fm-avatar>
      <fm-input
        v-model="commentForm.body" uid="body" type="textarea" class="flex-grow"
        rows="2" placeholder="Leave a comment" @focus="isCommentBoxFocused = true;" @blur="isCommentBoxFocused = false;"></fm-input>
    </div>
    <div v-if="commentForm.body || isCommentBoxFocused" class="text-right mt-3">
      <fm-button type="primary" native-type="submit">Comment</fm-button>
    </div>
  </fm-form>
  <div v-else-if="$auth.loggedIn" class="post-body mt-4 mb-8">
    <div class="py-4 bg-gray-100 text-center rounded-xl">
      <!-- TODO: sub-route and redirect to memberships tab and open the minimum_membership tier -->
      <!-- <fm-button @click="$router.push({ name: 'login' })">Become a member to comment</fm-button> -->
    </div>
  </div>
  <div v-else class="post-body mt-4 mb-8">
    <div class="py-4 bg-gray-100 text-center rounded-xl">
      <!-- TODO: sub-route and redirect to memberships tab and open the minimum_membership tier -->
      <fm-button @click="$router.push({ name: 'login' })">Become a member to comment</fm-button>
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
import { mapActions } from 'vuex';
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
    }
  }
};
</script>

<style>

</style>
