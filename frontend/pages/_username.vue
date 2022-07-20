<template>
<div v-if="user" v-loading="isLoading" class="bg-white" :class="{ 'disable-donation-and-join': isPreviewMode }">

  <!-- sticky header start -->
  <header v-show="showStickyNav" class="bg-white fixed z-20 top-0 w-full border-b animatecss animatecss-slideInDown" style="animation-duration: 100ms;">
    <div class="lg:container px-4 lg:px-0 flex items-center py-2">

      <breakpoint-helper></breakpoint-helper>

      <fm-avatar :src="user.avatar && user.avatar.medium" :name="user.display_name" size="w-8 h-8 lg:w-10 lg:h-10" class="flex-shrink-0"></fm-avatar>

      <div class="ml-2 lg:ml-3 mr-auto max-w-[60%] md:max-w-[50%]">
        <div v-tooltip="user.display_name" class="text-base lg:text-lg text-black font-bold leading-none lg:leading-none max-w-max truncate">{{ user.display_name }}</div>
        <div v-if="user.one_liner" v-tooltip="user.one_liner" class="mt-1 text-xs lg:text-sm text-gray-500 max-w-max truncate">{{ user.one_liner }}</div>
      </div>

      <fm-input :value="activeTab" type="select" size="sm" class="mx-4 hidden md:block" @change="gotoTab($event.target.value)">
        <option disabled>Jump to</option>
        <option :value="tabName.POSTS">Feed</option>
        <option :value="tabName.TIERS">Memberships</option>
        <option :value="tabName.DONATION">Donations</option>
      </fm-input>

      <fm-button :type="user.is_following ? 'success' : 'primary'" class="w-36 hidden md:block" :loading="isFollowLoading" @click="toggleFollow">
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

  <profile-above-the-tab v-intersect="handleIntersect" @add-post="addPost.isVisible = true;"></profile-above-the-tab>

  <fm-tabs ref="tabs" v-model="activeTab" centered class="mt-2" :class="{ 'min-h-[400px]': isLoading }">

    <fm-tabs-pane :id="tabName.POSTS" lazy label="Feed" class="bg-gray-50 pb-10">
      <div class="container min-h-[300px]">
        <div class="max-w-6xl row gx-0 lg:gx-4 mx-auto flex-wrap-reverse">
          <div class="col-12 lg:col-7">

            <div>
              <div v-if="profilePosts.results.length">
                <profile-post
                  v-for="post in profilePosts.results" :key="post.id"
                  :post="post" :hide-options="isPreviewMode" class="mb-6 md:mb-8"
                  @share-click="handleShareClick" @subscribe-click="handleSubscribeClick">
                </profile-post>
              </div>
              <div v-if="profilePosts.next" class="text-center mt-4">
                <fm-button :loading="nextPostsLoading" @click="loadNextPostsLocal">Load more</fm-button>
              </div>

              <!-- no posts action start -->
              <fm-card
                v-else-if="isSelfProfile && !profilePosts.results.length"
                class="mx-auto overflow-hidden" body-class="text-center !pt-16 !pb-20">
                <icon-image-plus class="h-16 w-16 stroke-1 animatecss animatecss-tada"></icon-image-plus>
                <div class="mt-2">
                  Post exclusive and private content of any type for your fans and keep in touch by interacting with them using comments.
                </div>
                <fm-button class="mt-4 min-w-[200px]" type="primary" @click="addPost.isVisible = true;">
                  Add a post
                </fm-button>
              </fm-card>
              <!-- no posts action end -->

              <!-- no posts public start -->
              <div v-else-if="!isSelfProfile && !profilePosts.results.length" class="italic text-center text-gray-500">
                {{ user.display_name }} hasn't posted anything yet.
              </div>
              <!-- no posts public end -->
            </div>
          </div>
          <div v-if="user.about || isSelfProfile" class="col-12 lg:col-5">
            <fm-card body-class="" class="overflow-hidden sticky top-20">
              <div class="text-xl text-black font-bold mb-3">About</div>
              <div v-if="user.about">
                <!-- TODO: remove duplication once breakpoint service is available -->
                <fm-read-more lines="2" class="lg:hidden mb-4">
                  <fm-markdown-styled>
                    <div v-html="user.about"></div>
                  </fm-markdown-styled>
                </fm-read-more>
                <fm-read-more lines="6" class="hidden lg:block mb-4">
                  <fm-markdown-styled>
                    <div v-html="user.about"></div>
                  </fm-markdown-styled>
                </fm-read-more>
              </div>
              <div
                v-else
                class="mx-auto overflow-hidden text-center pt-10 pb-14">
                <icon-scroll class="h-16 w-16 stroke-1"></icon-scroll>
                <div class="mt-2">
                  Start by telling your fans a bit about yourself and where they can find you.

                  <div class="text-sm text-gray-500 mt-3">
                    Click on <span class="text-black">Edit Page</span> to get started.
                  </div>

                </div>
              </div>
              <div class="flex justify-center space-x-4 text-gray-600">
                <a v-if="user.social_links.website_url" class="unstyled hover:text-gray-800" title="Website" target="_blank" :href="user.social_links.website_url">
                  <icon-globe :size="24"></icon-globe>
                </a>
                <a v-if="user.social_links.twitter_url" class="unstyled hover:text-gray-800" title="Twitter" target="_blank" :href="user.social_links.twitter_url">
                  <icon-twitter :size="24"></icon-twitter>
                </a>
                <a v-if="user.social_links.youtube_url" class="unstyled hover:text-gray-800" title="Youtube" target="_blank" :href="user.social_links.youtube_url">
                  <icon-youtube :size="24"></icon-youtube>
                </a>
                <a v-if="user.social_links.instagram_url" class="unstyled hover:text-gray-800" title="Instagram" target="_blank" :href="user.social_links.instagram_url">
                  <icon-instagram :size="24"></icon-instagram>
                </a>
                <a v-if="user.social_links.facebook_url" class="unstyled hover:text-gray-800" title="Facebook" target="_blank" :href="user.social_links.facebook_url">
                  <icon-facebook :size="24"></icon-facebook>
                </a>
              </div>
            </fm-card>
          </div>
        </div>
      </div>
    </fm-tabs-pane>

    <fm-tabs-pane
      v-if="shouldShowTiersTab"
      :id="tabName.TIERS" lazy label="Memberships" class="pb-10 bg-gray-50">
      <div class="container min-h-[300px]">
        <div class="max-w-6xl mx-auto">
          <div class="row justify-center gy-4 px-4">
            <div v-for="tier in user.tiers" :key="tier.id" class="col-12 md:col-6 lg:col-4">
              <profile-tier-card
                class="max-w-sm mx-auto h-full"
                v-bind="{ tier, loading: loadingTierId === tier.id }"
                @subscribe-click="handleSubscribeClick(tier)">
              </profile-tier-card>
            </div>
          </div>

          <!-- no tier action start -->
          <fm-card
            v-if="!user.tiers.length"
            class="mx-auto max-w-xl overflow-hidden" body-class="text-center !pt-16 !pb-20">
            <icon-crown class="h-16 w-16 stroke-1 animatecss animatecss-tada"></icon-crown>
            <div class="mt-2">
              Make a steady monthly income while offering exclusive content and experience based on membership tiers to your fans.
            </div>
            <nuxt-link :to="{ name: 'members-tiers', params: { add: '1' } }">
              <fm-button type="primary" class="mt-4">Create your first tier &rarr;</fm-button>
            </nuxt-link>
          </fm-card>
          <!-- no tier action end -->

        </div>
      </div>
    </fm-tabs-pane>

    <fm-tabs-pane :id="tabName.DONATION" lazy label="Donations" class="bg-gray-50 pb-10">
      <div class="container min-h-[300px]">
        <div class="row gx-0 lg:gx-4 max-w-6xl mx-auto justify-center">
          <div v-if="donations" class="col-12 order-2 lg:col-7 lg:order-1">
            <hr class="mt-6 mb-8 lg:hidden">
            <div class="text-xl font-bold mb-4">Recent donations</div>
            <fm-lazy v-for="(donation, idx) in donations" :key="donation.id"
              :class="{ 'mb-4 lg:mb-6': idx !== donations.length - 1 }" min-height="100">
              <profile-donation :donation="donation">
              </profile-donation>
            </fm-lazy>
            <div v-if="!donations.length" class="text-gray-500 text-center max-w-md mx-auto my-24">
              <template v-if="isSelfProfile">
                Your recent donations will show up here.
              </template>
              <template v-else>
                Become the first one to show your support for {{ user.display_name }}. Your contribution will show up here.
              </template>
            </div>
          </div>
          <div class="col-12 order-1 mb-6 sm:col-10 md:col-8 lg:col-5 lg:order-2 lg:mb-0">
            <donation-widget
              ref="donationWidget" :user="user" :loading="donationLoading"
              class="donation-card-sticky"
              @donate-click="handleDonateClick">
            </donation-widget>
          </div>
        </div>
      </div>
    </fm-tabs-pane>

  </fm-tabs>

  <!-- footer start -->
  <footer class="py-4 px-6 text-center">
    <div class="text-sm ml-7">Powered by</div>
    <nuxt-link to="/" class="mx-auto inline-block">
      <logo class="h-6"></logo>
    </nuxt-link>
  </footer>
  <!-- footer end -->

  <!-- phone bottom pane tab nav start -->
  <nav class="bottom-0 sticky z-20 w-full bg-white border-t md:hidden py-1 shadow">
    <ul class="flex items-center h-full max-w-full sm:max-w-md md:max-w-lg mx-2 sm:mx-auto justify-around">
      <li class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <div
          class="unstyled rounded-xl focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          :class="{ 'text-white bg-fm-primary pointer-events-none': activeTab === tabName.POSTS }"
          @click="gotoTab(tabName.POSTS)">

          <icon-image class="h-6 w-6"></icon-image>
          <div class="mt-1 truncate" title="Feed">Feed</div>
        </div>
      </li>
      <li v-if="shouldShowTiersTab" class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <div
          class="unstyled rounded-xl focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          :class="{ 'text-white bg-fm-primary pointer-events-none': activeTab === tabName.TIERS }"
          @click="gotoTab(tabName.TIERS)">

          <icon-crown class="h-6 w-6"></icon-crown>
          <div class="mt-1 truncate" title="Feed">Memberships</div>
        </div>
      </li>
      <li class="mx-2 cursor-pointer text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <div
          class="unstyled rounded-xl focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          :class="{ 'text-white bg-fm-primary pointer-events-none': activeTab === tabName.DONATION }"
          @click="gotoTab(tabName.DONATION)">

          <icon-coins class="h-6 w-6"></icon-coins>
          <div class="mt-1 truncate" title="Feed">Donations</div>
        </div>
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

  <profile-add-post v-if="isSelfProfile" v-model="addPost.isVisible"></profile-add-post>

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
    const tabName = {
      POSTS: 'posts',
      TIERS: 'tiers',
      DONATION: 'donation'
    };
    return {
      tabName,
      showStickyNav: false,
      activeTab: null,
      isLoading: true, // NOT being used. Use it if profile loading becomes slow
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
      this.activeTab = this.tabName.TIERS;
      this.handleSubscribeClick(routeData.tier);
      this.setGlobalLoader(false);
    } else {
      this.activeTab = (() => {
        if (this.currentUserHasActiveSubscription || this.isSelfProfile) return this.tabName.POSTS;
        if (this.shouldShowTiersTab) return this.tabName.TIERS;
        return this.tabName.DONATION;
      })();
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
    ...mapGetters('profile', ['isSelfProfile', 'currentUserHasActiveSubscription']),
    ...mapGetters('posts', ['profilePosts']),

    shouldShowTiersTab() {
      if (!this.user) return false;
      const hasTiers = !!this.user.tiers.length;
      return this.isSelfProfile || hasTiers;
    }
  },
  mounted() {
    loadRazorpay();
  },
  methods: {
    ...mapActions('profile', ['fetchProfile', 'createOrGetMembership', 'createDonation', 'processPayment', 'follow', 'unfollow']),
    ...mapActions('posts', ['loadNextProfilePosts']),
    ...mapMutations('ui', ['setGlobalLoader']),

    gotoTab(tabId) {
      this.activeTab = tabId;
      this.$refs.tabs.$el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    // logic is documented in createOrGetMembership
    async handleSubscribeClick(tier) {
      if (!this.$auth.loggedIn) {
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
        return;
      }

      const membership = data.scheduled_subscription;

      if (!membership) {
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
        this.donationLoading = false;
        const { error, response } = await this.processPayment({ donationOrSubscription, paymentResponse, supportType });
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
          this.loadingTierId = null;
          this.donationLoading = false;
        }
      };
      const rzp1 = new window.Razorpay(paymentOptions);

      // TODO: handle error in a more fancy way
      // failed
      rzp1.on('payment.failed', (response) => {
        // response.error.description, response.error.reason
        this.loadingTierId = null;
        this.donationLoading = false;
      });
      rzp1.open();
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
        this.$router.push({ name: 'set-password-token', params: { token: base64.encode(fanUser.email) } });
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
</style>
