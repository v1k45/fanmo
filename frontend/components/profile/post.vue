<template>
<div class="bg-white rounded-xl border pt-4 pb-1">
  <div class="post-body">
    <div class="flex items-center">
      <div class="flex flex-wrap flex-grow mr-auto">
        <nuxt-link
          :to="{ name: 'p-slug-id', params: { slug: post.slug, id: post.id } }"
          class="w-full basis-auto unstyled" title="Open post">
          <div class="text-lg md:text-xl text-black font-bold w-full">{{ post.title }}</div>
        </nuxt-link>
      </div>

      <!-- options for self profile start -->
      <div v-if="!hideOptions && isSelfProfile" class="ml-2 flex-shrink-0 self-start mt-0.5">
        <fm-dropdown placement="bottom-end">
          <button class="hover:text-fm-primary hover:scale-105 transform flex" title="Options">
            <span class="sr-only">Options</span>
            <icon-more-vertical class="h-6 w-6 text-gray-500"></icon-more-vertical>
          </button>
          <template #items>
            <fm-dropdown-item type="error" @click="deletePostLocal">Delete</fm-dropdown-item>
          </template>
        </fm-dropdown>
      </div>
      <!-- options for self profile end -->
    </div>
    <div class="flex flex-wrap items-center mt-1 text-xs">

      <!-- avatar and name start -->
      <nuxt-link
        :to="`/${post.author_user.username}/`"
        class="unstyled flex items-center mr-auto mt-1 overflow-hidden md:max-w-[47.5%]">
        <!-- avatar start -->
        <fm-avatar
          :src="post.author_user.avatar && post.author_user.avatar.small"
          :name="post.author_user.display_name"
          size="w-5 h-5 flex-shrink-0">
        </fm-avatar>
        <!-- avatar end -->

        <!-- name start -->
        <div class="ml-2 min-w-0 text-sm truncate">
          <div class="truncate" :title="post.author_user.display_name">{{ post.author_user.display_name }}</div>
        </div>
        <!-- name end -->
      </nuxt-link>
      <!-- avatar and name end -->

      <!-- TODO: show post visibility information for members too -->
      <div class="ml-7 md:ml-0 flex items-center text-gray-500 overflow-hidden mt-1 md:max-w-[47.5%]">
        <div class="text-gray-500 flex-shrink-0">{{ createdAt }}</div>
        <span class="mx-2">&bull;</span>
        <div
          v-tooltip="{ content: normalizedVisibility, disabled: post.visibility === 'public' }"
          tabindex="0" class="truncate">
          <icon-lock v-if="post.visibility !== 'public'" class="h-em w-em -mt-1"></icon-lock>
          <icon-globe v-if="post.visibility === 'public'" class="h-em w-em -mt-1"></icon-globe>
          {{ normalizedVisibility }}
        </div>
      </div>
    </div>
  </div>


  <template v-if="post.content">
    <div v-if="post.content.text" class="post-body">
      <fm-read-more-height :max-height="$route.name == 'p-slug-id' ? null : '200'" class="mt-4">
        <fm-markdown-styled>
          <div v-html="post.content.text"></div>
        </fm-markdown-styled>
      </fm-read-more-height>
    </div>

    <fm-carousel v-if="images.length" :images="images" class="mt-4"></fm-carousel>

    <div v-if="post.content.type === 'link'" class="post-body">
      <fm-markdown-styled class="mt-4">
        <a :href="post.content.link" target="_blank" rel="noopener noreferrer nofollow">{{ post.content.link }}</a>
      </fm-markdown-styled>
      <div v-if="post.content.link_embed" class="mt-4 aspect-w-16 aspect-h-9" v-html="post.content.link_embed.html">
      </div>
      <a
        v-else-if="post.content.link_og && linkPreviewOGComputed"
        class="unstyled block border overflow-hidden rounded-lg bg-gray-50 mt-3"
        :href="linkPreviewOGComputed.link" target="_blank" rel="noopener noreferrer nofollow">
        <div v-if="linkPreviewOGComputed.image" class="overflow-hidden flex-none">
          <img :src="linkPreviewOGComputed.image" class="w-full max-h-48 object-cover" alt="">
        </div>
        <div class="p-4 pt-3 flex-grow overflow-hidden">
          <div class="block font-bold max-w-full">{{ linkPreviewOGComputed.title }}</div>
          <div v-if="linkPreviewOGComputed.description" class="mt-1 text-sm">{{ linkPreviewOGComputed.description }}</div>
          <div class="text-gray-500 text-sm mt-1">{{ linkPreviewOGComputed.hostname }}</div>
        </div>
      </a>
    </div>
  </template>
  <div v-else-if="post.minimum_tier" class="mt-6 min-h-[300px] bg-gradient-to-tr from-fm-primary-400 to-fm-primary-700 flex items-center justify-center">
    <div class="text-center text-white">
      <icon-lock class="h-16 w-16 animatecss animatecss-shake animatecss-delay-3s"></icon-lock>
      <div class="mt-4 px-4">
        Join <strong>{{ post.minimum_tier.name }}</strong> to unlock this post now!
      </div>
      <div class="mt-6 rounded-l-full rounded-r-full">
        <fm-button
          type="" class="text-body" block @click="handleSubscribeIntent">
          Join now for {{ $currency(post.minimum_tier.amount) }}/month
        </fm-button>
      </div>
    </div>
  </div>

  <hr v-if="!images.length && post.content" class="mt-4">
  <div class="mt-4 mb-3 post-body flex items-center">
    <button type="link" class="inline-flex items-center mr-6" @click="toggleReaction('heart')">
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
    <button type="link" class="inline-flex items-center mr-auto" @click="handleCommentClick">
      <icon-message-square class="inline mr-2 h-em w-em"></icon-message-square>
      <template v-if="post.stats.comment_count">{{ post.stats.comment_count }}</template>
      <template v-else>Comment</template>
    </button>
    <button type="link" class="inline-flex items-center" @click="$emit('share-click', post)">
      <icon-share class="inline mr-2 h-em w-em"></icon-share>
      Share
    </button>
  </div>

  <slot name="bottom"></slot>
</div>
</template>

<script>
import dayjs from 'dayjs';
import get from 'lodash/get';
import { mapActions, mapMutations } from 'vuex';

export default {
  props: {
    post: { type: Object, required: true },
    showCreatorInfo: { type: Boolean, default: false },
    hideOptions: { type: Boolean, default: false } // useful for profile page to hide the post options when preview mode is active
  },
  data() {
    return {
      likedInThisSession: false
    };
  },
  computed: {
    isSelfProfile() {
      return !!(
        (get(this.$auth, 'user.username') && this.post.author_user.username) &&
        (this.$auth.user.username === this.post.author_user.username)
      );
    },

    createdAt() {
      if (!this.post || !this.post.created_at) return '';
      return dayjs(this.post.created_at).format('D MMM, YYYY hh:mm A');
    },
    normalizedVisibility() {
      const visibilityMap = {
        public: 'Public',
        all_members: 'All members',
        allowed_tiers: this.post.allowed_tiers.map(tier => tier.name).join(', ')
      };
      return visibilityMap[this.post.visibility];
    },
    images() {
      if (!this.post || !this.post.content || !this.post.content.files) return [];
      return this.post.content.files.filter(file => file.type === 'image').map(file => file.image.full);
    },
    linkPreviewOGComputed() {
      const { content } = this.post;
      if (content.type !== 'link') return null;
      // eslint-disable-next-line camelcase
      const { link, link_og } = content;
      const title = get(link_og, 'og.title') || get(link_og, 'meta.twitter:title') || link_og.page.title;
      const description = get(link_og, 'og.description') || get(link_og, 'meta.twitter:description') || get(link_og, 'meta.description') || '';
      const image = get(link_og, 'og.image') || get(link_og, 'meta.og:image') || '';
      return {
        link: link.toString(),
        hostname: (new URL(link)).hostname,
        title,
        description,
        image
      };
    },
    reaction() {
      // { heart: { isReacted, count } }
      return this.post.stats.reactions.reduce((acc, { emoji, is_reacted: isReacted, count }) => ({
        ...acc,
        [emoji]: { isReacted, count }
      }), { heart: { isReacted: false, count: 0 } });
    }
  },
  methods: {
    ...mapActions('posts', ['deletePost', 'addOrRemoveReaction']),
    ...mapMutations('ui', ['setGlobalLoader']),

    async deletePostLocal() {
      try {
        await this.$confirm.error('Are you sure you want to delete this post? This action is irreversible.', 'Confirm');
      } catch (err) {
        return;
      }
      const { success } = await this.deletePost(this.post.id);
      if (success) {
        this.$toast.info('Your post was deleted successfully.');
        this.$emit('deleted');
      }
    },
    async toggleReaction(emoji = 'heart') {
      if (!this.$auth.loggedIn) return this.$router.push({ name: 'login' });
      const action = this.reaction[emoji].isReacted ? 'remove' : 'add';
      await this.addOrRemoveReaction({
        postId: this.post.id,
        action,
        emoji
      });
      this.likedInThisSession = action === 'add';
    },
    handleCommentClick() {
      this.$router.push({ name: 'p-slug-id', params: { slug: this.post.slug, id: this.post.id } });
    },
    handleSubscribeIntent() {
      if (this.$route.name === 'username') { // on profile page, simply emit and the page can handle the rest
        this.$emit('subscribe-click', this.post.minimum_tier);
        return;
      }
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
.post-body {
  @apply px-4 sm:px-5 md:px-6;
}
</style>
