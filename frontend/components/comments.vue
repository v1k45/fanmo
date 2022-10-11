<template>
<div class="flex" :class="{'flex-col': inputFirst, 'flex-col-reverse': !inputFirst}">
  <fm-form v-if="canComment" class="mt-4" :errors="commentErrors" @submit.prevent="createCommentLocal">
    <div class="flex">
      <fm-avatar
        :src="$auth.user.avatar && $auth.user.avatar.small"
        :name="$auth.user.display_name"
        :size="`${size == 'sm' ? 'w-6 h-6' : 'w-12 h-12'} sm:w-8 sm:h-8 flex-shrink-0 mr-6`">
      </fm-avatar>
      <fm-input
        v-model="commentForm.body" uid="body" type="textarea" class="flex-grow"
        :size="size"
        :rows="size == 'sm' ? '1' : '2'" placeholder="Leave a comment" @focus="isCommentBoxFocused = true;" @blur="isCommentBoxFocused = false;"></fm-input>
    </div>
    <div v-if="commentForm.body || isCommentBoxFocused" class="text-right mt-3">
      <fm-button type="primary" native-type="submit" :size="size">Comment</fm-button>
    </div>
  </fm-form>

  <slot v-else name="locked">
  </slot>

  <div v-if="comments.length" class="border-t mt-4">
    <comment
      v-for="comment in (comments || [])"
      :key="comment.id"
      :comment="comment"
      :post="post"
      :donation="donation"
      :can-comment="canComment"
      :size="size"
      :input-first="inputFirst"
      :is-nested="!!donationId"
      class="mt-4">
    </comment>

    <div v-if="hasMoreComments" class="text-center my-6">
      <fm-button type="link" :loading="nextCommentsLoading" @click="loadNextCommentsLocal">Load more comments</fm-button>
    </div>
  </div>
</div>
</template>

<script>
import get from 'lodash/get';
import { mapActions, mapState } from 'vuex';
export default {
  props: {
    post: { type: Object, default: null },
    donation: { type: Object, default: null },
    size: { type: String, default: 'md' },
    inputFirst: { type: Boolean, default: true }
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
  computed: {
    ...mapState('comments', ['postCommentsMap', 'donationCommentsMap', 'commentsById']),
    canComment() {
      if (this.post) return this.post.can_comment;
      return this.donation.can_comment;
    },
    postId() {
      return get(this.post, 'id');
    },
    donationId() {
      return get(this.donation, 'id');
    },
    comments() {
      let commentIds = [];
      if (this.postId) {
        commentIds = get(this.postCommentsMap, `${this.postId}.commentIds`, []);
      } else if (this.donationId) {
        commentIds = get(this.donationCommentsMap, `${this.donationId}.commentIds`, []);
      }
      return commentIds.map(commentId => this.commentsById[commentId]).filter(comment => !!comment);
    },
    hasMoreComments() {
      if (this.postId) {
        return get(this.postCommentsMap, `${this.postId}.next`, false);
      }
      return get(this.donationCommentsMap, `${this.donationId}.next`, false);
    }
  },
  mounted() {
    // do not load donation comments if it is hidden and current user is not authorized to comment.
    if (this.donation && (this.donation.is_hidden && !this.canComment)) return;
    // do not load comments if we already know there are no comments.
    if (this.post && !this.post.stats.comment_count) return;
    if (this.donation && !this.donation.stats.comment_count) return;
    this.loadComments({ postId: this.postId, donationId: this.donationId });
  },
  methods: {
    ...mapActions('comments', ['createComment', 'loadComments', 'loadNextComments']),
    async createCommentLocal() {
      const { success, data } = await this.createComment({ postId: this.postId, donationId: this.donationId, body: this.commentForm.body, pushToTop: this.inputFirst });
      if (!success) this.commentErrors = data;
      else {
        this.commentForm.body = '';
        this.commentErrors = {};
      }
    },
    async loadNextCommentsLocal() {
      this.nextCommentsLoading = true;
      await this.loadNextComments({ postId: this.postId, donationId: this.donationId });
      this.nextCommentsLoading = false;
    }
  }
};
</script>

