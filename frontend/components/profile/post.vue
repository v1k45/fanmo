<template>
<div class="bg-white rounded-xl border pt-4 pb-1 relative">
  <div v-if="post.is_pinned" class="absolute right-0 top-0 flex">
    <div
      v-tooltip="'This is a pinned post.'"
      class="p-1 rounded-bl-lg rounded-tr-lg text-xs bg-fm-success-600 border-2 border-fm-success-600 border-r-0 border-t-0 text-white text-center right-0 top-0">
      <icon-pin class="h-em w-em"></icon-pin>
    </div>
  </div>
  <div class="post-body">
    <div class="flex items-center" :class="{'mb-3': $route.name == 'p-slug-id'}">
      <div class="flex flex-wrap flex-grow mr-auto">
        <nuxt-link v-if="post.section" :to="{ name: 'username-s-slug', params: { username: post.author_user.username, slug: post.section.slug } }" class="text-sm font-thin my-1 unstyled hover:text-gray-600 text-gray-500">{{ post.section.title }}</nuxt-link>
        <nuxt-link
          :to="{ name: 'p-slug-id', params: { slug: post.slug, id: post.id } }"
          class="w-full basis-auto unstyled" title="Open post">
          <div class="text-xl hover:text-gray-700 text-gray-800 font-bold w-full" :class="{'md:text-3xl': $route.name == 'p-slug-id', 'md:text-2xl': $route.name !== 'p-slug-id'}">{{ post.title }}</div>
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
            <fm-dropdown-item @click="togglePin"><icon-pin class="h-em w-em"></icon-pin> {{ post.is_pinned ? 'Unpin' : 'Pin' }}</fm-dropdown-item>
            <fm-dropdown-item @click="$router.push({ name: 'posts-id-edit', params: { id: post.id } })"><icon-edit class="h-em w-em"></icon-edit> Edit</fm-dropdown-item>
            <fm-dropdown-item type="error" @click="deletePostLocal"><icon-trash-2 class="h-em w-em"></icon-trash-2> Delete</fm-dropdown-item>
          </template>
        </fm-dropdown>
      </div>
      <!-- options for self profile end -->
    </div>
    <div class="flex flex-wrap items-center mt-1 text-xs">

      <!-- avatar and name start -->
      <nuxt-link
        :to="`/${post.author_user.username}/`"
        class="unstyled flex items-center mr-auto mt-1 overflow-hidden md:max-w-[47.5%] text-gray-600 hover:text-gray-500">
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
      <fm-read-more-height :max-height="$route.name == 'p-slug-id' ? null : '300'" :route="{ name: 'p-slug-id', params: { slug: post.slug, id: post.id } }" class="pt-2 mt-4 border-t border-gray-200">
        <fm-markdown-styled>
          <div class="whitespace-pre-line" v-html="post.content.text"></div>
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
          <img :src="linkPreviewOGComputed.image" class="w-full max-h-64 object-cover" alt="">
        </div>
        <div class="p-4 pt-3 flex-grow overflow-hidden">
          <div class="block font-bold max-w-full">{{ linkPreviewOGComputed.title }}</div>
          <div v-if="linkPreviewOGComputed.description" class="mt-1 text-sm">{{ linkPreviewOGComputed.description }}</div>
          <div class="text-gray-500 text-sm mt-1">{{ linkPreviewOGComputed.hostname }}</div>
        </div>
      </a>
    </div>
  </template>
  <div v-else class="mt-6 min-h-[450px] bg-gradient-to-tr from-gray-400 to-gray-700 flex items-center justify-center relative">
    <div class="absolute inset-0">
      <div class="relative h-full w-full">
        <img v-if="post.author_user.cover" :src="post.author_user.cover.medium" class="object-cover object-center w-full h-full" alt="">
        <div class="w-full h-full backdrop-blur-lg bg-gray-500/50 absolute inset-0"></div>
      </div>
    </div>
    <div v-if="!showPurchaseForm" class="text-center text-white m-2 md:m-4 z-10">
      <icon-lock class="h-16 w-16 animatecss animatecss-shake animatecss-delay-3s"></icon-lock>
      <template v-if="post.minimum_tier">
        <div class="mt-4 px-4">
          Join <strong>{{ post.minimum_tier.name }}</strong> to unlock this post now!
        </div>
        <div class="mt-6 rounded-l-full rounded-r-full px-4">
          <fm-button
            type="primary" class="text-body" :loading="joinActionLoading" block @click="handleSubscribeIntent">
            <icon-crown class="h-em w-em"></icon-crown>
            Join now for {{ $currency(post.minimum_tier.amount) }}/month
          </fm-button>
        </div>
      </template>
      <!-- super edge case when a user does not have a tier, but has Members Only posts. -->
      <div v-else class="mt-4 px-4">
        Become a member to unlock this post now!
      </div>
      <template v-if="post.is_purchaseable">
        <div class="mt-4 rounded-l-full rounded-r-full px-4">
          <fm-button
            type="" class="text-body" :loading="donationLoading" block @click="handlePurchaseIntent">
            <icon-coins class="h-em w-em"></icon-coins>
            Unlock with a {{ $currency(post.minimum_amount) }} tip
          </fm-button>
        </div>
      </template>
    </div>
    <div v-if="showPurchaseForm" v-loading="loading" class="max-w-lg w-full m-2 md:m-4 overflow-auto z-10">
      <post-donation :post="post" :user="post.author_user" :loading="donationLoading" @donate-click="handleDonateClick" @cancel="showPurchaseForm = false">
      </post-donation>

      <!-- dialogs start -->
      <profile-express-checkout
        v-model="expressCheckout.isVisible"
        :user="post.author_user"
        :tier="expressCheckout.tier"
        :post="post"
        :donation-data="expressCheckout.donationData"
        :support-type="expressCheckout.supportType"
        @submit="handleExpressCheckoutSubmit">
      </profile-express-checkout>

      <profile-payment-success
        v-model="paymentSuccess.isVisible"
        :tier="paymentSuccess.tier"
        :user="post.author_user"
        :post="post"
        :support-type="paymentSuccess.supportType"
        :success-message="paymentSuccess.successMessage"
        :donation-data="paymentSuccess.donationData"
        @dashboard-click="handlePaymentSuccessNext('dashboard')"
        @authenticated-next-click="handlePaymentSuccessNext('authenticated-next')"
        @unauthenticated-next-click="handlePaymentSuccessNext('unauthenticated-next')"
        @donation-close-click="handlePaymentSuccessNext('donation-close')">
      </profile-payment-success>

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
import { base64 } from '~/utils';


const MEMBERSHIP = 'membership';
const DONATION = 'donation';


export default {
  props: {
    post: { type: Object, required: true },
    showCreatorInfo: { type: Boolean, default: false },
    hideOptions: { type: Boolean, default: false }, // useful for profile page to hide the post options when preview mode is active
    joinActionLoading: { type: Boolean, default: false } // whether the join button should be in loading state
  },
  data() {
    return {
      likedInThisSession: false,
      showPurchaseForm: false,
      expressCheckout: {
        isVisible: false,
        tier: null,
        supportType: null,
        donationData: null
      },
      paymentSuccess: {
        isVisible: false,
        fanUser: null, // stores fan_user to facilitate the "Activate account" functionality during express checkout success
        successMessage: null,
        tier: null,
        donationData: null,
        supportType: null
      },
      donationLoading: false,
      loadingLockedPostId: null,
      loadingTierId: null,
      loading: false
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
      return this.post.content.files.filter(file => file.type === 'image').map(file => file.image);
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
    ...mapActions('posts', ['updatePost', 'deletePost', 'addOrRemoveReaction']),
    ...mapActions('profile', ['fetchProfileUser', 'fetchProfile', 'createDonation', 'processPayment']),
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
    async togglePin() {
      const { success, data } = await this.updatePost({ postId: this.post.id, payload: { is_pinned: !this.post.is_pinned } });
      if (success) {
        this.$toast.success(`This post is now ${data.is_pinned ? 'pinned' : 'unpinned'}.`);
      } else {
        this.$toast.error(get(data, 'is_pinned[0].message'));
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
      if (this.$route.name.startsWith('username')) { // on profile page, simply emit and the page can handle the rest
        this.$emit('subscribe-click', this.post.minimum_tier);
        return;
      }
      this.setGlobalLoader('Just a moment...');
      this.$router.push({
        name: 'username-memberships',
        params: {
          username: this.post.author_user.username,
          data: {
            intent: 'subscribe-through-post',
            tier: this.post.minimum_tier
          }
        }
      });
    },
    handlePurchaseIntent() {
      this.showPurchaseForm = true;
    },
    async handleDonateClick(donationData) {
      if (!this.$auth.loggedIn) {
        this.expressCheckout = {
          isVisible: true,
          tier: null,
          donationData,
          supportType: DONATION
        };
        return;
      }

      this.donationLoading = true;
      const { success, data } = await this.createDonation(donationData);
      if (!success) {
        if (data.message) data.non_field_errors = data.message;
        else if (data.amount) data.non_field_errors = data.amount;
        if (get(data, 'creator_username[0]')) this.$toast.error(data.creator_username[0].message);
        else this.$toast.error(data);
        this.donationLoading = false;
        return;
      }
      const donation = data;
      this.initiateRazorpayPayment(donation, DONATION, data);
    },

    handleExpressCheckoutSubmit(membershipOrDonationResponse) {
      const type = this.expressCheckout.supportType;
      this.expressCheckout = {
        isVisible: false,
        tier: null,
        supportType: null,
        donationData: null
      };
      this.initiateRazorpayPayment(
        type === MEMBERSHIP ? membershipOrDonationResponse.scheduled_subscription : membershipOrDonationResponse,
        type,
        membershipOrDonationResponse
      );
    },

    initiateRazorpayPayment(donationOrSubscription, supportType, donationOrSubscriptionResponse) {
      const paymentOptions = donationOrSubscription.payment.payload;
      // success
      paymentOptions.handler = async (paymentResponse) => {
        this.loadingTierId = null;
        this.loadingLockedPostId = null;
        this.donationLoading = false;
        this.loading = 'Processing payment... Do not close or refresh this page.';
        const { error, response } = await this.processPayment({ donationOrSubscription, paymentResponse, supportType });
        this.loading = false;
        if (error) {
          // TODO: add a retry option to the dialog
          this.$alert.error(response, 'Error');
          return;
        }
        if (this.$refs.donationWidget) this.$refs.donationWidget.reset();
        this.paymentSuccess = {
          isVisible: true,
          fanUser: donationOrSubscriptionResponse.fan_user,
          successMessage: response.message,
          tier: supportType === MEMBERSHIP ? donationOrSubscription.tier : null,
          donationData: supportType === DONATION ? donationOrSubscription : null,
          supportType
        };
      };
      // cancel
      paymentOptions.modal = {
        ondismiss: () => {
          this.loadingLockedPostId = null;
          this.loadingTierId = null;
          this.donationLoading = false;
        }
      };
      const rzp1 = new window.Razorpay(paymentOptions);

      // TODO: handle error in a more fancy way
      // failed
      rzp1.on('payment.failed', (response) => {
        this.loadingLockedPostId = null;
        this.loadingTierId = null;
        this.donationLoading = false;
        this.logApplicationEvent(
          'payment_failed',
          response,
          supportType === DONATION ? donationOrSubscription.id : null,
          supportType === MEMBERSHIP ? donationOrSubscription.id : null
        );
      });
      rzp1.open();
    },

    async logApplicationEvent(name, payload, donationId, subscriptionId) {
      try {
        await this.$axios.$post('/api/events/', {
          name, payload, donation_id: donationId, subscription_id: subscriptionId
        });
      } catch (err) {
        // do nothing
      }
    },

    handlePaymentSuccessNext(actionType) {
      const fanUser = this.paymentSuccess.fanUser;
      this.paymentSuccess = {
        isVisible: false,
        fanUser: null,
        successMessage: null,
        tier: null,
        donationData: null,
        supportType: null
      };
      if (actionType === 'dashboard') this.$router.push('dashboard');
      else if (actionType === 'authenticated-next') {
        this.fetchProfile(this.user.username);
        this.activeTab = this.tabName.POSTS;
      } else if (actionType === 'unauthenticated-next') {
        // set password
        this.$router.push({
          name: 'set-password-token',
          params: { token: base64.encode(fanUser.email), next: { name: 'p-slug-id', params: { slug: this.post.slug, id: this.post.id } } },
          query: { s: '1' }
        });
      } else if (actionType === 'donation-close') {
        // go to post detail page if already authentioated
        // refresh post to show updated info
        if (this.$route.name === 'p-slug-id') {
          this.$router.go(0);
        } else {
          this.$router.push({ name: 'p-slug-id', params: { slug: this.post.slug, id: this.post.id } });
        }
      }
    }
  }
};
</script>

<style>
.post-body {
  @apply px-4 sm:px-5 md:px-6;
}
</style>
