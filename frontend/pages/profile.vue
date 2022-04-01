<template>
<div v-if="user">
  <profile-above-the-tab></profile-above-the-tab>

  <div class="container">
    <fm-tabs v-model="activeTab" centered class="mt-8">
      <fm-tabs-pane :id="tabName.POSTS" lazy label="Posts" class="grid grid-cols-12 gap-5 pb-10">
        <div class="col-span-12 md:col-span-7">

          <div class="mt-8">
            <div class="flex flex-wrap items-center">
              <h1 class="text-2xl font-bold mr-auto">Posts</h1>
              <button v-if="$auth.loggedIn && user.username == $auth.user.username" class="mt-4 sm:mt-0 btn btn-wide btn-black" @click="isAddPostVisible = true;">
                <IconPlus class="mr-1" :size="16"></IconPlus>
                Add a post
              </button>
            </div>
            <div v-if="posts && posts.count" class="mt-8">
              <post v-for="post in posts.results" :key="post.id" :post="post" class="mb-6"></post>
            </div>
          </div>
        </div>
        <div class="col-span-12 md:col-span-5 h-full">
          <fm-card body-class="bg-gray-100 text-gray-600" class="overflow-hidden sticky top-20">
            <fm-read-more v-if="user.about" lines="6" class="mb-4">
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
      </fm-tabs-pane>

      <fm-tabs-pane :id="tabName.TIERS" lazy label="Memberships" class="row justify-center pb-10">

        <div class="max-w-6xl">
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
      </fm-tabs-pane>

      <fm-tabs-pane :id="tabName.DONATION" lazy label="Donations" class="row max-w-6xl mx-auto bg-yellow-50 justify-end pb-10">
        <div v-if="donations && donations.count" class="col-12 md:col-7">
          <div class="row justify-center">
            <donation v-for="donation in donations.results" :key="donation.id" :donation="donation">
            </donation>
          </div>
        </div>
        <div class="col-12 md:col-5">
          <div class="row justify-center">
            <donation-form :user="user" @donated="prependDonation"></donation-form>
          </div>
        </div>
      </fm-tabs-pane>
    </fm-tabs>
  </div>


  <add-post v-model="isAddPostVisible" @created="prependPost"></add-post>
  <profile-express-checkout
    v-model="expressCheckout.isVisible"
    :tier="expressCheckout.tier"
    :support-type="expressCheckout.supportType"
    @submit="handleExpressCheckoutSubmit">
  </profile-express-checkout>


  <profile-payment-success
    v-model="paymentSuccess.isVisible"
    :tier="paymentSuccess.tier"
    :support-type="paymentSuccess.supportType"
    :donation-amount="paymentSuccess.donationAmount"
    @dashboard-click="handlePaymentSuccessNext('dashboard')"
    @authenticated-next-click="handlePaymentSuccessNext('authenticated-next')"
    @unauthenticated-next-click="handlePaymentSuccessNext('unauthenticated-next')"
    @donation-close-click="handlePaymentSuccessNext('donation-close')">
  </profile-payment-success>
</div>
</template>

<script>
import {
  Plus as IconPlus
} from 'lucide-vue';
import { mapActions, mapGetters, mapState } from 'vuex';
import { loadRazorpay } from '~/utils';

export default {
  components: {
    IconPlus
  },
  layout:
    'default-no-container',
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
      isAddPostVisible: false,
      isLoading: true, // NOT being used. Use it if profile loading becomes slow
      expressCheckout: {
        isVisible: false,
        tier: null,
        supportType: null
      },
      paymentSuccess: {
        isVisible: false,
        tier: null,
        donationAmount: null,
        supportType: null
      },
      loadingTierId: null
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
    ...mapGetters('profile', ['isSelfProfile', 'currentUserHasActiveSubscription'])
  },
  mounted() {
    loadRazorpay();
  },
  methods: {
    ...mapActions('profile', ['fetchProfile', 'createOrGetMembership', 'processPayment']),

    async handleSubscribeClick(tier) {
      if (!this.$auth.loggedIn) {
        this.expressCheckout = {
          isVisible: true,
          tier,
          supportType: 'membership'
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
          tier,
          donationAmount: null,
          supportType: 'membership'
        };
        return;
      }

      this.initiateRazorpayPayment(membership);
    },

    handleExpressCheckoutSubmit(membership) {
      this.expressCheckout = {
        isVisible: false,
        tier: null,
        supportType: null
      };
      this.initiateRazorpayPayment(membership);
    },

    initiateRazorpayPayment(subscription) {
      const paymentOptions = subscription.payment.payload;
      // success
      paymentOptions.handler = async (paymentResponse) => {
        this.loadingTierId = null;
        const err = await this.processPayment({ subscription, paymentResponse });
        if (err) {
          // TODO: add a retry option to the dialog
          this.$alert.error(err, 'Error');
          return;
        }
        this.paymentSuccess = {
          isVisible: true,
          tier: subscription.tier,
          donationAmount: null,
          supportType: 'membership'
        };
      };
      // cancel
      paymentOptions.modal = {
        ondismiss: () => {
          this.loadingTierId = null;
        }
      };
      const rzp1 = new window.Razorpay(paymentOptions);

      // TODO: handle error in a more fancy way
      // failed
      rzp1.on('payment.failed', (response) => {
        this.loadingTierId = null;
        // this.$alert.error(err);
        // alert(response.error.description);
        // alert(response.error.reason);
      });
      rzp1.open();
    },

    handlePaymentSuccessNext(actionType) {
      this.paymentSuccess = {
        isVisible: false,
        tier: null,
        donationAmount: null,
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

    prependPost(post) {
      this.posts.results.unshift(post);
    },
    prependDonation(donation) {
      this.donations.results.unshift(donation);
    }
  }
};
</script>
