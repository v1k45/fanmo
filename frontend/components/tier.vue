<template>
<!-- TODO: move layout/column to the consumer content -->
<div class="col-12 sm:col-6 md:col-6 lg:col-4 xl:col-3 self-stretch" style="min-height: 350px;">
  <div class="card compact border shadow-lg relative min-h-full">
    <div v-if="tier.is_public === false" class="absolute top-0 right-1">
      <span class="badge badge-warning">Private</span>
    </div>
    <!-- <figure class="aspect-w-4 aspect-h-2 relative">
      <img src="https://picsum.photos/200/100" class="absolute top-0 left-0 h-full w-full object-cover">
    </figure> -->
    <div class="card-body flex-grow-0">
      <h2 class="card-title text-center">
        <icon-indian-rupee class="inline h-6"></icon-indian-rupee>{{ tier.amount }}
        <div class="text-base truncate">{{ tier.name }}</div>
      </h2>
    </div>
    <div v-if="!isSubscribing" class="card-body pt-0 flex-grow justify-start">
      <p class="mt-2">{{ tier.description }}</p>
      <ul class="list-disc list-inside text-left mt-3 mb-auto">
        <li v-for="(benefit, index) in tier.benefits" :key="index">
          {{ benefit }}
        </li>
      </ul>
      <div class="justify-center card-actions">
        <button v-if="selfMode" class="btn btn-block btn-info" @click="$emit('edit', tier)">Edit</button>
        <button v-else class="btn btn-block" @click="toggleIsSubscribing">Subscribe</button>
      </div>
    </div>
    <div v-if="isSubscribing" class="card-body pt-0">
      <fm-form :errors="subscriptionErrors" @submit.prevent="subscribe">
        <fm-input v-if="!$auth.loggedIn" v-model="subscriptionForm.email" uid="email" class="max-w-md" placeholder="Your email" name="email"></fm-input>
        <div class="justify-center card-actions">
          <button class="btn btn-block">Pay</button>
          <button class="btn btn-block btn-ghost" @click="toggleIsSubscribing">Cancel</button>
        </div>
      </fm-form>
    </div>
  </div>
</div>
</template>

<script>
export default {
  props: {
    selfMode: { type: Boolean, default: false }, // shows the option to edit instead of subscribing
    user: {
      type: Object
    },
    tier: {
      type: Object
    }
  },
  data() {
    return {
      isSubscribing: false,
      subscriptionForm: {
        creator_username: this.user.username,
        tier_id: this.tier.id,
        email: ''
      },
      subscriptionErrors: {}
    };
  },
  methods: {
    async subscribe() {
      this.$toast.info('Starting payment intent');
      let membership;
      try {
        const existingMembership = await this.$axios.$get(
          '/api/memberships/',
          { params: { creator_username: this.user.username } }
        );
        if (existingMembership.results.length) {
          membership = await this.$axios.$patch(
            `/api/memberships/${existingMembership.results[0].id}/`,
            this.subscriptionForm
          );
        } else {
          membership = await this.$axios.$post(
            '/api/memberships/',
            this.subscriptionForm
          );
        }
      } catch (err) {
        this.subscriptionErrors = err.response.data;
        console.error(err.response.data);
        return;
      }

      // start payment intent if required
      if (membership.scheduled_subscription.payment.is_required) {
        // TODO: if there is an active subscription
        // let the user know that they are going to pay only Rs. 5 for authorizating the transaction.
        // it sill be automatically refunded and the actual subscription amount will be charged
        // when the next subscription cycle starts.
        this.startPayment(membership.scheduled_subscription);
      }
    },
    startPayment(subscription) {
      const paymentOptions = subscription.payment.payload;
      paymentOptions.handler = (paymentResponse) => {
        this.processPayment(subscription, paymentResponse);
      };
      const rzp1 = new window.Razorpay(paymentOptions);
      rzp1.open();
    },
    async processPayment(subscription, paymentResponse) {
      try {
        await this.$axios.$post('/api/payments/', {
          processor: 'razorpay',
          type: 'subscription',
          subscription_id: subscription.id,
          payload: paymentResponse
        });
        this.$toast.success('Payment successful.');
      } catch (err) {
        console.error(err.response.data);
        this.subscriptionErrors = err.response.data;
        this.subscriptionErrors.non_field_errors = [
          {
            message:
              'There was an error while processing the payment. If money was deducted from your account, it will be automatically refunded in 2 days. Feel free to contact us if you have any questions.'
          }
        ];
      }
    },
    toggleIsSubscribing() {
      this.isSubscribing = !this.isSubscribing;
      if (!this.isSubscribing) this.subscriptionErrors = {};
    }
  }
};
</script>
