<template>
<div v-if="user" class="bg-white">
  <profile-above-the-tab></profile-above-the-tab>

  <fm-tabs v-model="activeTab" centered class="mt-8">
    <fm-tabs-pane :id="tabName.POSTS" lazy label="Posts" class="bg-gray-50 pb-10">
      <div class="container min-h-[300px]">
        <div class="max-w-6xl row gx-0 lg:gx-4 mx-auto flex-wrap-reverse">
          <div class="col-12 lg:col-7">

            <div class="mt-6">
              <div v-if="isSelfProfile" class="text-right mb-6">
                <fm-button type="info" @click="addPost.isVisible = true;">
                  <icon-plus class="mr-1" :size="16"></icon-plus>
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
            </div>
          </div>
          <div class="col-12 lg:col-5">
            <fm-card body-class="" class="overflow-hidden sticky top-20 mt-6">
              <div class="text-xl text-black font-bold mb-3">About me</div>
              <!-- TODO: remove duplication once breakpoint service is available -->
              <fm-read-more v-if="user.about" lines="2" class="lg:hidden mb-4">
                <p v-html="user.about"></p>
              </fm-read-more>
              <fm-read-more v-if="user.about" lines="6" class="hidden lg:block mb-4">
                <p v-html="user.about"></p>
              </fm-read-more>
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

    <fm-tabs-pane :id="tabName.TIERS" lazy label="Memberships" class="pb-10 bg-gray-50">
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
        </div>
      </div>
    </fm-tabs-pane>

    <fm-tabs-pane :id="tabName.DONATION" lazy label="Donations" class="bg-gray-50 pb-10">
      <div class="container min-h-[300px]">
        <div class="row gx-0 lg:gx-4 max-w-6xl mx-auto justify-center">
          <div v-if="donations && donations.length" class="col-12 order-2 lg:col-7 lg:order-1">
            <hr class="mt-6 mb-8 lg:hidden">
            <div class="text-xl font-bold mb-4">Recent donations ({{ donations.length }})</div>
            <fm-lazy v-for="(donation, idx) in donations" :key="donation.id"
              :class="{ 'mb-4 lg:mb-6': idx !== donations.length - 1 }" min-height="100">
              <profile-donation :donation="donation">
              </profile-donation>
            </fm-lazy>
            <div v-if="!donations.length" class="mt-8 text-gray-500">Nothing to see here yet.</div>
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
    :support-type="paymentSuccess.supportType"
    :success-message="paymentSuccess.successMessage"
    :donation-data="paymentSuccess.donationData"
    @dashboard-click="handlePaymentSuccessNext('dashboard')"
    @authenticated-next-click="handlePaymentSuccessNext('authenticated-next')"
    @unauthenticated-next-click="handlePaymentSuccessNext('unauthenticated-next')"
    @donation-close-click="handlePaymentSuccessNext('donation-close')">
  </profile-payment-success>

  <profile-add-post v-if="isSelfProfile" v-model="addPost.isVisible"></profile-add-post>

  <profile-share v-model="sharePost.isVisible" :text="sharePost.text" :url="sharePost.url"></profile-share>
</div>
</template>

<script>
import {
  Plus as IconPlus
} from 'lucide-vue';
import { mapActions, mapGetters, mapState } from 'vuex';
import { loadRazorpay } from '~/utils';

const MEMBERSHIP = 'membership';
const DONATION = 'donation';

export default {
  components: {
    IconPlus
  },
  layout: 'default-no-container',
  props: {
    username: {
      type: String,
      default: null
    }
  },
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
        url: null,
        text: null
      }
    };
  },
  async fetch() {
    const username = this.username || this.$auth.user.username;
    this.isLoading = true;
    await this.fetchProfile(username);
    this.activeTab = this.currentUserHasActiveSubscription ? this.tabName.POSTS : this.tabName.TIERS;
    this.isLoading = false;
  },
  head: {
    title: 'My profile'
  },
  computed: {
    ...mapState('profile', ['user', 'donations', 'posts']),
    ...mapGetters('profile', ['isSelfProfile', 'currentUserHasActiveSubscription']),
    ...mapGetters('posts', ['profilePosts'])
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
        this.$toast.error(data);
        this.loadingTierId = null;
        return;
      }

      const membership = data;

      if (!membership) {
        this.paymentSuccess = {
          isVisible: true,
          successMessage: 'Your membership level was scheduled to update. Changes will be reflected during the next subscription cycle.',
          tier,
          donationData: null,
          supportType: 'membership'
        };
        return;
      }

      this.initiateRazorpayPayment(membership, MEMBERSHIP);
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
        this.$toast.error(data);
        this.donationLoading = false;
        return;
      }
      const donation = data;
      this.initiateRazorpayPayment(donation, DONATION);
    },

    handleExpressCheckoutSubmit(membershipOrDonation) {
      const type = this.expressCheckout.supportType;
      this.expressCheckout = {
        isVisible: false,
        tier: null,
        supportType: null,
        donationData: null
      };
      this.initiateRazorpayPayment(membershipOrDonation, type);
    },

    initiateRazorpayPayment(donationOrSubscription, supportType) {
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
      this.paymentSuccess = {
        isVisible: false,
        successMessage: null,
        tier: null,
        donationData: null,
        supportType: null
      };
      if (actionType === 'dashboard') this.$router.push('dashboard');
      else if (actionType === 'authenticated-next') {
        this.fetchProfile(this.user.username);
        this.activeTab = this.tabName.POSTS;
      } else if (actionType === 'unauthenticated-next') this.$router.push('login');
      else if (actionType === 'donation-close') {
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
        url: post.slug,
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
