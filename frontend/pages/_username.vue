<template>
<div v-if="user" v-loading="isLoading || showGlobalLoader" class="bg-white relative" :class="{ 'disable-donation-and-join': isPreviewMode }">
  <div v-if="loadingLockedPostId || loadingTierId" class="z-20 fixed h-full w-full top-0 left-0"></div>
  <!-- sticky header start -->
  <header v-show="showStickyNav" class="bg-white fixed z-20 top-0 w-full border-b animatecss animatecss-slideInDown" style="animation-duration: 100ms;">
    <div class="lg:container px-4 lg:px-0 flex items-center py-2">

      <breakpoint-helper></breakpoint-helper>

      <fm-avatar :src="user.avatar && user.avatar.medium" :name="user.display_name" size="w-8 h-8 lg:w-10 lg:h-10" class="flex-shrink-0"></fm-avatar>

      <div class="ml-2 lg:ml-3 mr-auto max-w-[60%] md:max-w-[50%]">
        <div v-tooltip="user.display_name" class="text-base lg:text-lg text-black font-bold leading-none lg:leading-none max-w-max truncate">{{ user.display_name }}</div>
        <div v-if="user.one_liner" v-tooltip="user.one_liner" class="mt-1 text-xs lg:text-sm text-gray-500 max-w-max truncate">{{ user.one_liner }}</div>
      </div>

      <div class="space-x-2 hidden md:block">
        <fm-button type="primary" @click="$router.push({ name: 'username-memberships', params: { username: user.username } })">
          <icon-crown class="h-em w-em"></icon-crown> Join
        </fm-button>
        <fm-button type="primary" @click="$router.push({ name: 'username-tips', params: { username: user.username } })">
          <icon-coins class="h-em w-em"></icon-coins> Tip
        </fm-button>
      </div>

      <fm-button v-if="false" :type="user.is_following ? 'success' : 'primary'" class="w-36 hidden md:block" :loading="isFollowLoading" @click="toggleFollow">
        <div v-if="user.is_following" class="flex items-center justify-center">
          <icon-check class="inline-block mr-1 h-em w-em flex-shrink-0"></icon-check> Following
        </div>
        <div v-else class="flex items-center justify-center">
          <icon-plus class="inline-block mr-1 h-em w-em flex-shrink-0"></icon-plus> Follow
        </div>
      </fm-button>

      <layout-navigation
        :type="$auth.loggedIn ? 'hamburger-minimal' : 'anonymous-hamburger'"
        class="rounded-full ml-4">
      </layout-navigation>
    </div>

  </header>
  <!-- sticky header end -->

  <profile-above-the-tab ref="above-the-tab" v-intersect="handleIntersect" @add-post="$router.push({ name: 'posts', params: { data: { intent: 'add' } } })"></profile-above-the-tab>

  <div class="mt-2 flex justify-center" :class="{ 'min-h-[400px]': isLoading }">
    <div class="flex xjustify-center max-w-full overflow-x-auto border-b">
      <div v-for="item in nav" :key="item.name" class="pb-1 bg-white group">
        <template v-if="!item.children">
          <nuxt-link
            :to="item.url" replace
            class="px-8 py-3 unstyled block relative font-medium text-gray-700 hover:text-gray-600 hover:bg-gray-100 rounded-t whitespace-nowrap"
            :class="{ 'hidden md:block': item.hideOnSM }"
            exact-active-class="!text-fm-primary font-bold">
            {{ item.label }}
            <div
              :class="{ 'bg-fm-primary': item.isActive, 'bg-white group-hover:bg-gray-100': !item.isActive }"
              class="absolute left-0 -bottom-1 w-full h-1"></div>
          </nuxt-link>
        </template>
        <template v-else>
          <fm-dropdown :class="{ 'md:hidden': item.hideOnMD }" placement="bottom">
            <div
              :class="{ '!text-fm-primary font-bold': item.isActive }"
              class="px-8 py-3 unstyled block relative font-medium text-gray-700 hover:text-gray-600 hover:bg-gray-100 rounded-t whitespace-nowrap">
              {{ item.label }} <icon-chevron-down class="inline-block h-4 w-4"></icon-chevron-down>
              <div
                :class="{ 'bg-fm-primary': item.isActive, 'bg-white group-hover:bg-gray-100': !item.isActive }"
                class="absolute left-0 -bottom-1 w-full h-1"></div>
            </div>
            <template #items>
              <fm-dropdown-item v-for="childItem in item.children" :key="childItem.name" class="max-w-[90vw] truncate" :active="childItem.isActive">
                <nuxt-link :to="childItem.url" class="w-full block unstyled" replace>
                  {{ childItem.label }}
                </nuxt-link>
              </fm-dropdown-item>
            </template>
          </fm-dropdown>
        </template>
      </div>
    </div>
  </div>

  <div class="bg-gray-50 pt-6 pb-10 min-h-[300px]">
    <nuxt-child
      :key="$route.path"
      :loading="isLoading"
      :donation-loading="donationLoading"
      :posts-loading="nextPostsLoading"
      :loading-locked-post-id="loadingLockedPostId"
      :loading-tier-id="loadingTierId"
      :is-preview-mode="isPreviewMode"
      @share="handleShareClick"
      @load-more-posts="loadNextPostsLocal"
      @subscribe="handleSubscribeClick"
      @donate="handleDonateClick">
    </nuxt-child>
  </div>

  <!-- footer start -->
  <footer class="pt-4 md:pb-4 pb-20 px-6 text-center">
    <div class="text-sm ml-7">Powered by</div>
    <nuxt-link to="/" class="mx-auto inline-block">
      <logo class="h-6"></logo>
    </nuxt-link>
  </footer>
  <!-- footer end -->

  <!-- phone bottom pane tab nav start -->
  <nav class="bottom-0 fixed z-20 w-full bg-white border-t md:hidden py-1 shadow">
    <ul class="flex items-center h-full max-w-full sm:max-w-md md:max-w-lg mx-2 sm:mx-auto justify-around">
      <li class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <nuxt-link
          class="unstyled rounded focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          exact-active-class="text-white bg-fm-primary pointer-events-none"
          :to="{ name: 'username', params: { username: user.username } }">
          <icon-image class="h-4 w-4"></icon-image>
          <div class="mt-1 truncate" title="Feed">Feed</div>
        </nuxt-link>
      </li>
      <li v-if="shouldShowTiersTab" class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <nuxt-link
          class="unstyled rounded focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          exact-active-class="text-white bg-fm-primary pointer-events-none"
          :to="{ name: 'username-memberships', params: { username: user.username } }">
          <icon-crown class="h-4 w-4"></icon-crown>
          <div class="mt-1 truncate" title="Feed">Memberships</div>
        </nuxt-link>
      </li>
      <li class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <nuxt-link
          class="unstyled rounded focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          exact-active-class="text-white bg-fm-primary pointer-events-none"
          :to="{ name: 'username-tips', params: { username: user.username } }">
          <icon-coins class="h-4 w-4"></icon-coins>
          <div class="mt-1 truncate" title="Feed">Tips</div>
        </nuxt-link>
      </li>
    </ul>
  </nav>
  <!-- phone bottom pane tab nav end -->

  <!-- dialogs start -->
  <profile-express-checkout
    v-model="expressCheckout.isVisible"
    :user="user"
    :tier="expressCheckout.tier"
    :donation-data="expressCheckout.donationData"
    :support-type="expressCheckout.supportType"
    @submit="handleExpressCheckoutSubmit">
  </profile-express-checkout>


  <profile-payment-success
    v-model="paymentSuccess.isVisible"
    :tier="paymentSuccess.tier"
    :user="user"
    :support-type="paymentSuccess.supportType"
    :success-message="paymentSuccess.successMessage"
    :donation-data="paymentSuccess.donationData"
    @dashboard-click="handlePaymentSuccessNext('dashboard')"
    @authenticated-next-click="handlePaymentSuccessNext('authenticated-next')"
    @unauthenticated-next-click="handlePaymentSuccessNext('unauthenticated-next')"
    @donation-close-click="handlePaymentSuccessNext('donation-close')">
  </profile-payment-success>

  <profile-share v-model="sharePost.isVisible" :text="sharePost.text" :relative-url="sharePost.relativeUrl"></profile-share>
  <!-- dialogs end -->
</div>
</template>

<script>
import get from 'lodash/get';
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
import { base64, loadRazorpay } from '~/utils';

const MEMBERSHIP = 'membership';
const DONATION = 'donation';

export default {
  layout: 'empty',
  data() {
    return {
      showStickyNav: false,
      isLoading: true,
      donationFormErrors: null,
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
      addPost: {
        isVisible: false
      },
      loadingTierId: null,
      loadingLockedPostId: null, // when someone clicks on Join on a locked post, this will store the id of the post to show the loading state on
      donationLoading: false,
      nextPostsLoading: false,
      isFollowLoading: false,

      sharePost: {
        isVisible: false,
        relativeUrl: null,
        text: null
      }
    };
  },
  async fetch() {
    const username = this.$route.params.username;
    this.isLoading = true;

    const { success, data } = await this.fetchProfile(username);
    if (!success) {
      if (data.some(d => get(d.data, 'responseStatusCode') === 404)) return this.$nuxt.error({ statusCode: 404 });
    }

    const routeData = (this.$route.params.data || {});
    if (routeData.intent === 'subscribe-through-post') {
      await this.handleSubscribeClick(routeData.tier);
      this.setGlobalLoader(false);
    }

    this.isLoading = false;
  },
  auth: false,
  head() {
    return {
      title: this.user ? this.user.display_name : this.$route.params.username
    };
  },
  computed: {
    ...mapState('profile', ['user', 'donations', 'posts', 'isPreviewMode']),
    ...mapState('ui', ['showGlobalLoader']),
    ...mapGetters('profile', ['isSelfProfile', 'currentUserHasActiveSubscription']),
    ...mapGetters('posts', ['profilePosts', 'sections']),

    shouldShowTiersTab() {
      if (!this.user) return false;
      const hasTiers = !!this.user.tiers.length;
      return this.isSelfProfile || hasTiers;
    },

    nav() {
      const routeName = this.$route.name;
      const sectionTabs = [];
      for (const section of this.sections.filter(s => s.show_in_menu)) {
        sectionTabs.push({
          name: `username-s-${section.slug}`,
          label: section.title,
          url: `/${this.user.username}/s/${section.slug}`,
          isActive: routeName === 'username-s-slug' && this.$route.params.slug === section.slug,
          hideOnSM: true,
          replace: true
        });
      }

      if (sectionTabs.length) {
        sectionTabs.push({
          name: 'username-s',
          label: 'Sections',
          url: `/${this.user.username}/s`,
          isActive: routeName === 'username-s-slug',
          hideOnMD: true,
          children: [...sectionTabs]
        });
      }

      return [
        { name: 'username', label: 'Feed', url: `/${this.user.username}`, isActive: routeName === 'username' },
        ...sectionTabs,
        { name: 'username-memberships', label: 'Memberships', url: `/${this.user.username}/memberships`, isActive: routeName === 'username-memberships', hideOnSM: true },
        { name: 'username-tips', label: 'Tips', url: `/${this.user.username}/tips`, isActive: routeName === 'username-tips', hideOnSM: true },
        { name: 'username-about', label: 'About', url: `/${this.user.username}/about`, isActive: routeName === 'username-about' }
      ];
    }
  },
  created() {
    loadRazorpay();
  },
  methods: {
    ...mapActions('profile', ['fetchProfile', 'createOrGetMembership', 'createDonation', 'processPayment', 'follow', 'unfollow']),
    ...mapActions('posts', ['loadNextProfilePosts']),
    ...mapMutations('ui', ['setGlobalLoader']),

    // logic is documented in createOrGetMembership
    async handleSubscribeClick(tier, { postId = null } = {}) {
      if (!this.currentUserHasActiveSubscription) {
        this.expressCheckout = {
          isVisible: true,
          tier,
          supportType: 'membership',
          donationData: null
        };
        return;
      }

      if (this.currentUserHasActiveSubscription) {
        try {
          await this.$confirm.warning(
            ['You already have an active membership with this creator.',
              'Switching the membership level will apply after the current cycle ends.',
              '<br><strong>Are you sure you want to continue?<strong>'].join('<br>'),
            'Confirm',
            { html: true }
          );
        } catch (err) {
          return;
        }
      }

      this.loadingLockedPostId = postId;
      this.loadingTierId = tier.id;
      const { success, data } = await this.createOrGetMembership({
        creator_username: this.user.username,
        tier_id: tier.id,
        period: this.$route.query.period
      });
      if (!success) {
        if (get(data, 'creator_username[0]')) this.$toast.error(data.creator_username[0].message);
        else this.$toast.error(data);
        this.loadingTierId = null;
        this.loadingLockedPostId = null;
        return;
      }

      const membership = data ? data.scheduled_subscription : null;

      if (!membership) {
        this.loadingTierId = null;
        this.loadingLockedPostId = null;
        this.donationLoading = false;

        this.paymentSuccess = {
          isVisible: true,
          successMessage: 'Your membership level was scheduled to update. Changes will be reflected during the next subscription cycle.',
          tier,
          fanUser: this.$auth.user,
          donationData: null,
          supportType: 'membership'
        };
        return;
      }

      this.initiateRazorpayPayment(membership, MEMBERSHIP, data);
    },

    async handleDonateClick(donationData) {
      if (!this.$auth.loggedIn) {
        this.expressCheckout = {
          isVisible: true,
          tier: null,
          donationData,
          supportType: 'donation'
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
        this.isLoading = 'Processing payment... Do not close or refresh this page.';
        const { error, response } = await this.processPayment({ donationOrSubscription, paymentResponse, supportType });
        this.isLoading = false;
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
        this.$router.push({
          name: 'username',
          params: { username: this.user.username }
        });
      } else if (actionType === 'unauthenticated-next') {
        this.$router.push({
          name: 'set-password-token',
          params: { token: base64.encode(fanUser.email) },
          query: { s: '1' }
        });
      } else if (actionType === 'donation-close') {
        this.fetchProfile(this.user.username);
      }
    },

    async loadNextPostsLocal() {
      this.nextPostsLoading = true;
      await this.loadNextProfilePosts();
      this.nextPostsLoading = false;
    },

    handleShareClick(post) {
      this.sharePost = {
        isVisible: true,
        relativeUrl: `p/${post.slug}/${post.id}`,
        text: post.title
      };
    },

    handleIntersect(entries, observer, isIntersecting) {
      this.showStickyNav = !isIntersecting;
    },

    async toggleFollow() {
      // TODO: redirect back to this after login and dispatch follow automatically
      if (!this.$auth.loggedIn) return this.$router.push('/login');
      this.isFollowLoading = true;
      if (this.user.is_following) await this.unfollow();
      else await this.follow();
      this.isFollowLoading = false;
    }
  }
};
</script>
<style lang="scss">
.donation-card-sticky {
  @apply lg:sticky lg:top-20;
}
@media (max-height: 600px) {
  .donation-card-sticky {
    @apply lg:max-h-[75vh] lg:overflow-auto;
  }
}

.disable-donation-and-join {
  .btn-join,
  .btn-rejoin,
  .btn-donate,
  .donation-card-sticky {
    @apply pointer-events-none cursor-not-allowed;
  }
}

.hide-tab-headers-on-phone {
  .fm-tabs__header {
    @apply hidden md:flex;
  }
}
</style>
