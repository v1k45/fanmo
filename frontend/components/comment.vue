<template>
<div class="flex">
  <fm-avatar
    :src="comment.author_user.avatar && comment.author_user.avatar.small"
    :name="comment.author_user.display_name"
    size="w-6 h-6 sm:w-8 sm:h-8 flex-shrink-0">
  </fm-avatar>
  <div class="ml-1 sm:ml-3 mr-auto flex-grow min-w-0 text-sm sm:text-base">
    <fm-read-more-height max-height="200">
      <div
        class="font-bold max-w-[75%] truncate float-left"
        :class="{ 'bg-fm-primary text-white px-2 sm:px-3 rounded-xl font-normal': creatorUser.username === comment.author_user.username }"
        :title="comment.author_user.name || comment.author_user.username">
        {{ comment.author_user.name || comment.author_user.username }}
      </div>
      <span class="ml-2 clear-both whitespace-pre-wrap">{{ comment.body }}</span>
    </fm-read-more-height>

    <div class="mt-1 flex items-end sm:items-center text-gray-500">
      <button type="link" class="inline-flex items-center mr-4" @click="toggleReaction('heart')">
        <icon-heart
          class="inline mr-2 h-em w-em animatecss"
          :class="{
            'text-fm-error fill-current': reaction.heart.isReacted,
            'animatecss-heartBeat': reaction.heart.isReacted && likedInThisSession
          }">
        </icon-heart>
        <template v-if="reaction.heart.count">{{ reaction.heart.count }}</template>
        <template v-else>Like</template>
      </button>
      <button v-if="!isNested" class="mr-4 flex-shrink-0" @click="handleReplyClick">
        Reply <template v-if="comment.children.length">({{ comment.children.length }})</template>
      </button>
      <button v-if="canDelete" class="text-fm-error flex-shrink-0 mr-4" @click="deleteCommentLocal">
        <span class="hidden sm:inline">Delete</span>
        <icon-trash class="sm:hidden h-em w-em"></icon-trash>
      </button>
      <span class="text-xs sm:text-sm truncate">{{ dayjs(comment.created_at).format('D MMM, YYYY hh:mma') }}</span>
    </div>

    <fm-form v-if="$auth.loggedIn && canComment && showReplyForm" :errors="commentErrors" class="mt-4" @submit.prevent="createReply">
      <div class="flex">
        <fm-avatar
          :src="$auth.user.avatar && $auth.user.avatar.small"
          :name="$auth.user.display_name"
          size="w-8 h-8 flex-shrink-0 mr-4">
        </fm-avatar>
        <fm-input
          v-model="commentForm.body" uid="body" type="textarea" class="flex-grow"
          :size="size"
          placeholder="Leave a comment" :rows="(isCommentTextareaFocused || commentForm.body) ? 2 : 1"
          @focus="isCommentTextareaFocused = true;" @blur="isCommentTextareaFocused = false;"></fm-input>
      </div>
      <div v-if="commentForm.body || isCommentTextareaFocused" class="text-right mt-3">
        <fm-button type="primary" native-type="submit" :size="size">Comment</fm-button>
      </div>
    </fm-form>

    <div v-if="!isNested" class="pt-2">
      <comment
        v-for="childComment in comment.children" :key="childComment.id"
        :size="size" :input-first="inputFirst"
        :post="post" :donation="donation" :comment="childComment" :parent-comment="comment" :can-comment="canComment" is-nested class="mt-4">
      </comment>

      <hr v-if="comment.children.length" class="mt-4">
    </div>


  </div>
</div>
</template>

<script>
import dayjs from 'dayjs';
import { mapActions } from 'vuex';
import get from 'lodash/get';
export default {
  props: {
    isNested: { type: Boolean, default: false },
    post: { type: Object, required: false, default: null },
    donation: { type: Object, required: false, default: null },
    comment: { type: Object, required: true },
    parentComment: { type: Object, default: null },
    canComment: { type: Boolean, default: false },
    size: { type: String, default: 'md' },
    inputFirst: { type: Boolean, default: false }
  },
  data() {
    return {
      dayjs,
      showReplyForm: false,
      commentErrors: {},
      isCommentTextareaFocused: false,
      likedInThisSession: false,
      commentForm: {
        body: ''
      }
    };
  },
  computed: {
    creatorUser() {
      return this.post ? this.post.author_user : this.donation.creator_user;
    },
    canDelete() {
      return this.$auth.loggedIn && (
        this.comment.author_user.username === this.$auth.user.username ||
            this.creatorUser.username === this.$auth.user.username
      );
    },

    reaction() {
      // { heart: { isReacted, count } }
      return this.comment.reactions.reduce((acc, { emoji, is_reacted: isReacted, count }) => ({
        ...acc,
        [emoji]: { isReacted, count }
      }), { heart: { isReacted: false, count: 0 } });
    }
  },
  methods: {
    ...mapActions('comments', ['createComment', 'deleteComment', 'addOrRemoveCommentReaction']),
    async createReply() {
      const { success, data } = await this.createComment({
        postId: get(this.post, 'id'),
        donationId: get(this.donation, 'id'),
        parentId: this.comment.id,
        body: this.commentForm.body,
        pushToTop: this.inputFirst
      });
      if (!success) this.commentErrors = data;
      else {
        this.commentForm.body = '';
        this.commentErrors = {};
        this.showReplyForm = false;
      }
    },

    handleReplyClick() {
      if (!this.$auth.loggedIn) return this.$router.push({ name: 'login' });
      this.showReplyForm = !this.showReplyForm;
    },

    async deleteCommentLocal() {
      try {
        await this.$confirm.error('Are you sure you want to delete this comment? This action is irreversible.', 'Confirm');
      } catch (err) {
        return;
      }
      const { success } = await this.deleteComment({
        parentId: get(this.parentComment, 'id'),
        commentId: this.comment.id
      });
      if (success) this.$toast.info('Your comment was deleted.');
    },
    async toggleReaction(emoji = 'heart') {
      if (!this.$auth.loggedIn) return this.$router.push({ name: 'login' });
      const action = this.reaction[emoji].isReacted ? 'remove' : 'add';
      await this.addOrRemoveCommentReaction({
        parentId: get(this.parentComment, 'id'),
        commentId: this.comment.id,
        action,
        emoji
      });
      this.likedInThisSession = action === 'add';
    }
  }
};
</script>

