<template>
<div v-if="user" class="bg-white">
  <profile-above-the-tab></profile-above-the-tab>

  <fm-tabs v-model="activeTab" centered class="mt-8">
    <fm-tabs-pane :id="tabName.POSTS" lazy label="Feed" class="bg-gray-50 pb-10">
      <div class="container min-h-[300px]">
        <div class="max-w-6xl row gx-0 lg:gx-4 mx-auto flex-wrap-reverse">
          <div class="col-12 lg:col-7">

            <div class="mt-6">
              <div v-if="isSelfProfile && profilePosts.results.length" class="text-right mb-6">
                <fm-button type="primary" @click="addPost.isVisible = true;">
                  <icon-image-plus class="mr-1" :size="16"></icon-image-plus>
                  Add a post
                </fm-button>
              </div>
              <div v-if="profilePosts.results.length">
                <profile-post
                  v-for="post in profilePosts.results" :key="post.id" :post="post"
                  class="mb-6 md:mb-8" @share-click="handleShareClick"></profile-post>
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
            <fm-card body-class="" class="overflow-hidden sticky top-20 mt-6">
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
          <div class="row justify-center mt-2 gy-4 px-4">
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

  <profile-express-checkout
    v-model="expressCheckout.isVisible"
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
</div>
</template>

<script>
import get from 'lodash/get';
import { mapActions, mapGetters, mapState } from 'vuex';
import { base64, loadRazorpay } from '~/utils';

const MEMBERSHIP = 'membership';
const DONATION = 'donation';

export default {
  layout: 'default-no-container',
  data() {
    const tabName = {
      POSTS: 'posts',
      TIERS: 'tiers',
      DONATION: 'donation'
    };
    return {
      tabName,
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
    await this.fetchProfile(username);
    this.activeTab = (() => {
      if (this.currentUserHasActiveSubscription || this.isSelfProfile) return this.tabName.POSTS;
      if (this.shouldShowTiersTab) return this.tabName.TIERS;
      return this.tabName.DONATION;
    })();
    this.isLoading = false;
  },
  auth: false,
  head() {
    return {
      title: this.user ? this.user.display_name : this.$route.params.username
    };
  },
  computed: {
    ...mapState('profile', ['user', 'donations', 'posts']),
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
    ...mapActions('profile', ['fetchProfile', 'createOrGetMembership', 'createDonation', 'processPayment']),
    ...mapActions('posts', ['loadNextProfilePosts']),

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
      const { success, data } = await this.createOrGetMembership({ creator_username: this.user.username, tier_id: tier.id });
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
        relativeUrl: post.slug,
        text: post.title
      };
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
</style>
