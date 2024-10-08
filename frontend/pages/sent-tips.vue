
<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <!-- header start -->
  <misc-page-header class="container sm:pl-0" :page="pages.sentDonations"></misc-page-header>
  <!-- header end -->

  <!-- container start -->
  <div v-if="donations" class="container mt-5 pt-6 pb-16 md:px-8 rounded-xl border bg-white">

    <!-- filters start -->
    <div class="flex flex-wrap w-full">

      <!-- search start -->
      <div class="mr-auto lg:max-w-sm flex-grow">
        <label class="text-sm block font-bold mb-2">Search for tips</label>
        <fm-input v-model="filter.search" placeholder="Search by creator name" @input="handleSearchInput">
          <template #prepend>
            <icon-search class="w-em"></icon-search>
          </template>
        </fm-input>
      </div>
      <!-- search end -->

      <div class="w-full mt-4 lg:hidden"></div>

      <!-- sort start -->
      <div class="w-full sm:w-[unset] lg:ml-4">
        <label class="text-sm block font-bold mb-2">Sort by</label>
        <fm-input v-model="filter.orderBy" type="select" @change="loadDonations">
          <option value="-created_at">Newest tip first</option>
          <option value="created_at">Oldest tip first</option>
          <option value="-amount">Highest tip first</option>
          <option value="amount">Lowest tip first</option>
          <option value="-lifetime_amount">Highest lifetime amount first</option>
          <option value="lifetime_amount">Lowest lifetime amount first</option>
        </fm-input>
      </div>
      <!-- sort end -->

    </div>
    <!-- filters end -->

    <!-- table start -->
    <fm-table class="mt-8 table-fixed lg:table-auto" first-column-sticky>
      <colgroup>
        <col class="w-[100px] md:min-w-[200px]"> <!-- creator -->
        <col class="min-w-[120px]"> <!-- amount -->
        <col> <!-- message -->
        <col class="min-w-[140px]"> <!-- lifetime amount -->
        <col class="min-w-[175px]"> <!-- date -->
        <col class="w-[100px]"> <!-- actions -->
      </colgroup>
      <thead>
        <tr class="text-xs uppercase">
          <th>Creator</th>
          <th class="!text-right">Amount</th>
          <th>Message</th>
          <th class="!text-right">Lifetime amount</th>
          <th>Date</th>
          <th></th>
        </tr>
      </thead>
      <tbody v-show="donations.results.length" class="text-sm">
        <tr v-for="donation in donations.results" :key="donation.id">
          <th>
            <nuxt-link :to="`/${donation.creator_user.username}`">
              <div class="flex items-center">
                <fm-avatar
                  :src="donation.creator_user.avatar && donation.creator_user.avatar.small"
                  :name="donation.creator_user.display_name"
                  size="w-5 h-5 lg:w-7 lg:h-7 mr-2 inline-block font-normal flex-shrink-0">
                </fm-avatar>
                <div class="max-w-[100px] lg:max-w-[200px] font-normal">
                  <div class="truncate text-xs lg:text-sm text-black" :title="donation.creator_user.display_name">{{ donation.creator_user.display_name }}</div>
                  <div v-if="donation.creator_user.one_liner" class="hidden lg:block truncate text-xs font-normal text-gray-500">{{ donation.creator_user.one_liner }}</div>
                </div>
              </div>
            </nuxt-link>
          </th>
          <td class="text-right">{{ $currency(donation.amount) }}</td>
          <td>
            <div class="truncate max-w-[200px]">
              <span v-if="donation.message && donation.is_hidden" title="Message is only visible to you and the creator.">
                <icon-eye-off class="w-4 h-4 text-gray-400 mr-1"></icon-eye-off>
              </span>
              <span :title="donation.message">{{ donation.message }}</span>
            </div>
          </td>
          <td class="text-right">{{ $currency(donation.lifetime_amount) }}</td>
          <td>{{ $datetime(donation.created_at) }}</td>
          <td class="text-center">
            <fm-button size="sm" @click="viewDonation(donation)">Details</fm-button>
          </td>
        </tr>
      </tbody>
    </fm-table>
    <div v-if="!donations.results.length" class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-b-lg border border-t-0">
      <div class="text-sm">
        <template v-if="hasActiveFilters">No results matched your filtering criteria.</template>
        <template v-else>You haven't given any tips yet.</template>
      </div>
    </div>
    <!-- table end -->

    <!-- next button start -->
    <div v-if="donations.next" class="text-center mt-4">
      <fm-button :loading="isNextDonationsLoading" @click="fetchMoreDonationsLocal(donations.next)">Load More</fm-button>
    </div>
    <!-- next button end -->
  </div>
  <!-- container end -->

  <!-- dialogs start -->
  <fm-dialog v-model="showDialog" drawer>
    <template #header>
      <div v-if="activeDonation" class="text-base">
        Tip details for {{ activeDonation.creator_user.display_name }}
      </div>
    </template>

    <template v-if="activeDonation">

      <!-- name, one liner and avatar start -->
      <nuxt-link :to="`/${activeDonation.creator_user.username}`">
        <div class="flex items-center">
          <fm-avatar
            :src="activeDonation.creator_user.avatar && activeDonation.creator_user.avatar.small"
            :name="activeDonation.creator_user.display_name"
            size="w-8 h-8 mr-2 inline-block font-normal flex-shrink-0">
          </fm-avatar>
          <div>
            <div class="text-black" :title="activeDonation.creator_user.display_name">{{ activeDonation.creator_user.display_name }}</div>
            <div v-if="activeDonation.creator_user.one_liner" class="text-xs font-normal text-gray-500">
              {{ activeDonation.creator_user.one_liner }}
            </div>
          </div>
        </div>
      </nuxt-link>
      <!-- name, one liner and avatar end -->

      <hr class="my-4">

      <!-- key value pairs start -->
      <dl>

        <!-- date start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Date</dt>
          <dd class="flex-grow">{{ $datetime(activeDonation.created_at) }}</dd>
        </div>
        <!-- date end -->

        <!-- amount start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Amount</dt>
          <dd class="flex-grow">{{ $currency(activeDonation.amount) }}</dd>
        </div>
        <!-- amount end -->

        <!-- lifetime amount start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Lifetime amount</dt>
          <dd class="flex-grow">{{ $currency(activeDonation.lifetime_amount) }}</dd>
        </div>
        <!-- lifetime amount end -->

        <!-- lifetime amount start -->
        <div v-if="activeDonation.post" class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Unlocked Post</dt>
          <dd class="flex-grow">
            <nuxt-link :to="{ name: 'p-slug-id', params: { slug: activeDonation.post.slug, id: activeDonation.post.id } }">{{ activeDonation.post.title }}</nuxt-link>
          </dd>
        </div>
        <!-- lifetime amount end -->

        <!-- message visibility start -->
        <div v-if="activeDonation.message" class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Message visibility</dt>
          <dd class="flex items-center flex-grow flex-wrap">
            <div class="mr-auto">{{ activeDonation.is_hidden ? 'Only visible to you and the creator' : 'Visible to everyone' }}</div>
          </dd>
        </div>
        <!-- message visibility end -->


        <!-- message start -->
        <div class="mb-2" data-swipe-ignore>
          <dt class="text-sm text-gray-500">Message <icon-corner-right-down class="h-em w-em"></icon-corner-right-down></dt>
          <dd class="border rounded-lg p-3 mt-4">
            <fm-read-more-height v-if="activeDonation.message" max-height="200">
              <div class="whitespace-pre-wrap overflow-auto">{{ activeDonation.message }}</div>
            </fm-read-more-height>
            <div v-else class="text-gray-600 text-sm italic">No message was included with this tip.</div>
          </dd>
        </div>
        <!-- message end -->

      </dl>
      <!-- key value pairs end -->

      <hr class="my-4">

      <!-- comments start -->
      <h3 class="font-medium">Comments</h3>
      <comments :donation="activeDonation" size="sm" :input-first="false"></comments>
      <!-- comments end -->

      <hr class="my-4">

      <!-- payment history table start -->
      <h3 class="font-medium">Payment History <template v-if="payments && payments.count">({{ payments.count }})</template></h3>
      <fm-table class="mt-4">
        <thead>
          <tr class="text-xs uppercase">
            <th>Date</th>
            <th class="!text-right">Amount</th>
            <th>Method</th>
            <th>Transaction ID</th>
          </tr>
        </thead>
        <tbody v-if="payments" class="text-sm">
          <tr v-for="payment in payments.results" :key="payment.id">
            <td><span class="whitespace-nowrap">{{ $datetime(payment.created_at) }}</span></td>
            <td class="text-right">{{ $currency(payment.amount) }}</td>
            <td>{{ payment.method }}</td>
            <td><code class="text-xs">{{ payment.external_id }}</code></td>
          </tr>
        </tbody>
      </fm-table>
      <div v-if="!payments || !payments.results.length" class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-b-lg border border-t-0">
        <div class="text-sm">You haven't made any tip transactions yet.</div>
      </div>
      <!-- payment history table end -->

      <!-- nuxt button start -->
      <div v-if="payments && payments.next" class="text-center mt-4">
        <fm-button size="sm" :loading="isNextPaymentsLoading" @click="fetchMorePaymentsLocal(payments.next)">Load More</fm-button>
      </div>
      <!-- nuxt button end -->

    </template>
  </fm-dialog>
  <!-- dialogs end -->
</div>
</template>

<script>
import debounce from 'lodash/debounce';
import { mapActions, mapMutations, mapState } from 'vuex';

export default {
  layout: 'with-sidebar',
  data() {
    return {
      filter: {
        search: '',
        orderBy: '-created_at'
      },
      showDialog: false,
      activeDonation: null,
      isNextDonationsLoading: false,
      isNextPaymentsLoading: false
    };
  },
  head: {
    title: 'Sent tips'
  },
  computed: {
    ...mapState('donations', ['donations', 'payments']),
    ...mapState('ui', ['pages']),

    hasActiveFilters() {
      return !!(this.filter.search);
    }
  },
  created() {
    this.setCurrentPage('sentDonations');
    this.loadDonations();
  },
  methods: {
    ...mapActions('donations', ['fetchSentDonations', 'fetchMoreDonations', 'fetchPayments', 'fetchMorePayments']),
    ...mapMutations('ui', ['setCurrentPage']),

    handleSearchInput: debounce(function() {
      this.loadDonations();
    }, 250),
    loadDonations() {
      const params = { fan_username: this.$auth.user.username, ordering: this.filter.orderBy };
      if (this.filter.search) {
        params.search = this.filter.search;
      }
      this.fetchSentDonations(params);
    },
    viewDonation(donation) {
      this.activeDonation = donation;
      this.showDialog = true;
      this.fetchPayments({ relatedDonationId: donation.id });
    },
    async fetchMoreDonationsLocal(url) {
      this.isNextDonationsLoading = true;
      await this.fetchMoreDonations(url);
      this.isNextDonationsLoading = false;
    },
    async fetchMorePaymentsLocal(url) {
      this.isNextPaymentsLoading = true;
      await this.fetchMorePayments(url);
      this.isNextPaymentsLoading = false;
    }
  }
};
</script>
