<template>
<div class="flex">
  <fm-avatar
    :src="comment.author_user.avatar && comment.author_user.avatar.small"
    :name="comment.author_user.display_name"
    size="w-8 h-8 flex-shrink-0">
  </fm-avatar>
  <div class="ml-3 mr-auto flex-grow min-w-0">
    <fm-read-more-height max-height="200">
      <div
        class="font-bold max-w-[75%] truncate float-left"
        :class="{ 'bg-fm-primary text-white px-3 rounded-xl font-normal': post.author_user.username === comment.author_user.username }"
        :title="comment.author_user.name || comment.author_user.username">
        {{ comment.author_user.name || comment.author_user.username }}
      </div>
      <span class="ml-3 clear-both whitespace-pre-wrap">{{ comment.body }}</span>
    </fm-read-more-height>

    <div class="mt-1 flex items-center text-gray-500">
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
      <button v-if="!isNested" class="mr-4" @click="handleReplyClick">
        Reply <template v-if="comment.children.length">({{ comment.children.length }})</template>
      </button>
      <button v-if="canDelete" class="text-fm-error mr-4" @click="deleteCommentLocal">
        Delete
      </button>
      <span class="text-sm">{{ dayjs(comment.created_at).format('D MMM, YYYY hh:mma') }}</span>
    </div>


    <fm-form v-if="$auth.loggedIn && post.can_comment && showReplyForm" class="mt-4" @submit.prevent="createReply">
      <div class="flex">
        <fm-avatar
          v-if="$auth.loggedIn"
          :src="$auth.user.avatar && $auth.user.avatar.small"
          :name="$auth.user.name" :username="$auth.user.username"
          size="w-8 h-8 flex-shrink-0 mr-4">
        </fm-avatar>
        <fm-avatar v-else size="w-12 h-12 flex-shrink-0 mr-6"></fm-avatar>
        <fm-input
          v-model="commentForm.body" uid="body" type="textarea" class="flex-grow"
          placeholder="Leave a comment" :rows="(isCommentTextareaFocused || commentForm.body) ? 3 : 1"
          @focus="isCommentTextareaFocused = true;" @blur="isCommentTextareaFocused = false;"></fm-input>
      </div>
      <div v-if="commentForm.body || isCommentTextareaFocused" class="text-right mt-3">
        <fm-button type="primary" native-type="submit">Comment</fm-button>
      </div>
    </fm-form>

    <div v-if="!isNested" class="pt-2">
      <profile-comment
        v-for="childComment in comment.children" :key="childComment.id"
        :post="post" :comment="childComment" :parent-comment="comment" is-nested class="mt-4">
      </profile-comment>

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
    post: { type: Object, required: true },
    comment: { type: Object, required: true },
    parentComment: { type: Object, default: null }
  },
  data() {
    return {
      dayjs,
      showReplyForm: false,
      isCommentTextareaFocused: false,
      likedInThisSession: false,
      commentForm: {
        body: ''
      }
    };
  },
  computed: {
    canDelete() {
      return this.$auth.loggedIn && (
        this.comment.author_user.username === this.$auth.user.username ||
        this.post.author_user.username === this.$auth.user.username
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
    ...mapActions('posts', ['createComment', 'deleteComment', 'addOrRemoveCommentReaction']),
    async createReply() {
      const { success, data } = await this.createComment({ postId: this.post.id, parentId: this.comment.id, body: this.commentForm.body });
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
        await this.$confirm.warning('Are you sure you want to delete this comment? This action is irreversible.', 'Confirm');
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
