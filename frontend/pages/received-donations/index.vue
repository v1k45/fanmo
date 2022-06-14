<template>
<div v-if="donations">

  <div v-if="stats" class="flex text-center mb-6">
    <div>
      <div class="text-lg sm:text-3xl font-bold">{{ stats.total }}</div>
      <div class="text-xs sm:text-sm text-gray-600">total donations</div>
    </div>
    <div class="ml-3 sm:ml-10">
      <div class="text-lg sm:text-3xl font-bold">{{ stats.total_with_message }}</div>
      <div class="text-xs sm:text-sm text-gray-600">with message</div>
    </div>
    <div class="ml-3 sm:ml-10">
      <div class="text-lg sm:text-3xl font-bold">{{ stats.total_without_message }}</div>
      <div class="text-xs sm:text-sm text-gray-600">without message</div>
    </div>
    <div class="ml-3 sm:ml-10">
      <div class="text-lg sm:text-3xl font-bold">{{ $currency(stats.total_payment) }}</div>
      <div class="text-xs sm:text-sm text-gray-600">total payment</div>
    </div>
  </div>

  <!-- filters start -->
  <div class="flex flex-wrap w-full">

    <!-- search start -->
    <div class="mr-auto lg:max-w-sm flex-grow">
      <label class="text-sm block font-bold mb-2">Search for donations</label>
      <fm-input v-model="filter.search" placeholder="Search by name or email" @input="handleSearchInput">
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
        <option value="-created_at">Newest donation first</option>
        <option value="created_at">Oldest donation first</option>
        <option value="-amount">Highest donation first</option>
        <option value="amount">Lowest donation first</option>
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
      <col class="w-[100px] md:min-w-[200px]"> <!-- member -->
      <col class="min-w-[120px]"> <!-- amount -->
      <col class="min-w-[140px]"> <!-- lifetime amount -->
      <col>
      <col class="min-w-[175px]"> <!-- date -->
      <col class="w-[100px]"> <!-- actions -->
    </colgroup>
    <thead>
      <tr class="text-xs uppercase">
        <th>Supporter</th>
        <th class="!text-right">Amount</th>
        <th class="!text-right">Lifetime amount</th>
        <th>Message</th>
        <th>Date</th>
        <th></th>
      </tr>
    </thead>
    <tbody v-show="donations.results.length" class="text-sm">
      <tr v-for="donation in donations.results" :key="donation.id">
        <th>
          <div class="flex items-center">
            <fm-avatar
              :src="donation.fan_user.avatar && donation.fan_user.avatar.small"
              :name="donation.fan_user.display_name" :username="donation.fan_user.username"
              size="w-5 h-5 lg:w-7 lg:h-7 mr-2 inline-block font-normal flex-shrink-0">
            </fm-avatar>
            <div class="max-w-[100px] lg:max-w-[200px] font-normal">
              <div class="truncate text-xs lg:text-sm text-black" :title="donation.fan_user.display_name">{{ donation.fan_user.display_name }}</div>
              <div class="truncate text-xs font-normal text-gray-500">
                <a class="unstyled" :href="`mailto:${donation.fan_user.email}`">{{ donation.fan_user.email }}</a>
              </div>
            </div>
          </div>
        </th>
        <td class="text-right">{{ $currency(donation.amount) }}</td>
        <td class="text-right">{{ $currency(donation.lifetime_amount) }}</td>
        <td>
          <div class="truncate max-w-[200px]">
            <span v-if="donation.message && donation.is_hidden" title="Message is only visible to you and the supporter.">
              <icon-eye-off class="w-4 h-4 text-gray-400 mr-1"></icon-eye-off>
            </span>
            <span :title="donation.message">{{ donation.message }}</span>
          </div>
        </td>
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
      <template v-else>You don't have any donations yet.</template>
    </div>
  </div>
  <!-- table end -->

  <!-- next button start -->
  <div v-if="donations.next" class="text-center mt-4">
    <fm-button :loading="isNextDonationsLoading" @click="fetchMoreDonationsLocal(donations.next)">Load More</fm-button>
  </div>
  <!-- next button end -->

  <!-- dialogs start -->
  <fm-dialog v-model="showDialog" drawer>
    <template #header>
      <div v-if="activeDonation" class="text-base">
        Donation details for {{ activeDonation.fan_user.display_name }}
      </div>
    </template>

    <template v-if="activeDonation">
      <!-- name, email and avatar start -->
      <div class="flex items-center">
        <fm-avatar
          :src="activeDonation.fan_user.avatar && activeDonation.fan_user.avatar.small"
          :name="activeDonation.fan_user.display_name" :username="activeDonation.fan_user.username"
          size="w-8 h-8 mr-2 inline-block font-normal flex-shrink-0">
        </fm-avatar>
        <div>
          <div class="truncate text-black" :title="activeDonation.fan_user.display_name">{{ activeDonation.fan_user.display_name }}</div>
          <div class="truncate text-xs font-normal text-gray-500">
            <a class="unstyled" :href="`mailto:${activeDonation.fan_user.email}`">{{ activeDonation.fan_user.email }}</a>
          </div>
        </div>
      </div>
      <!-- name, email and avatar end -->

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

        <!-- message visibility start -->
        <div v-if="activeDonation.message" class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Message visibility</dt>
          <dd class="flex items-center flex-grow flex-wrap">
            <div class="mr-auto">{{ activeDonation.is_hidden ? 'Hidden' : 'Visible to everyone' }}</div>
            <fm-button
              type="info" size="sm" class="flex items-center"
              @click="toggleMessageVisibility(activeDonation)">
              <icon-eye class="h-em w-em mr-1"></icon-eye>
              {{ activeDonation.is_hidden ? 'Make public' : 'Make private' }}
            </fm-button>
          </dd>
        </div>
        <!-- message visibility end -->


        <!-- message start -->
        <div class="mb-2">
          <dt class="text-sm text-gray-500">Message <icon-corner-right-down class="h-em w-em"></icon-corner-right-down></dt>
          <dd class="border rounded-lg p-3 mt-4">
            <fm-read-more-height v-if="activeDonation.message" max-height="200">
              <div class="whitespace-pre-wrap overflow-auto">{{ activeDonation.message }}</div>
            </fm-read-more-height>
            <div v-else class="text-gray-600 text-sm italic">No message was included with this donation.</div>
          </dd>
        </div>
        <!-- message end -->

      </dl>
      <!-- key value pairs end -->

      <hr class="my-4">

      <!-- payment history table start -->
      <h3 class="font-medium">Payment History <template v-if="payments && payments.count">({{ payments.count }})</template></h3>
      <fm-table class="mt-4">
        <thead>
          <tr class="text-xs uppercase">
            <th>Date</th>
            <th class="!text-right">Amount</th>
            <th>Payout</th>
            <th>Transaction ID</th>
          </tr>
        </thead>
        <tbody v-if="payments" class="text-sm">
          <tr v-for="payment in payments.results" :key="payment.id">
            <td><span class="whitespace-nowrap">{{ $datetime(payment.created_at) }}</span></td>
            <td class="text-right">{{ $currency(payment.amount) }}</td>
            <td>
              <div class="flex items-center">
                <template v-if="payment.payout">
                  <div v-if="payment.payout.status === 'scheduled'" class="animate-pulse block h-em w-em rounded-full bg-gray-300 mr-2"></div>
                  <div v-else-if="payment.payout.status === 'processed'" class="block h-em w-em rounded-full bg-fm-warning mr-2"></div>
                  <div v-else-if="payment.payout.status === 'settled'" class="block h-em w-em rounded-full bg-fm-success mr-2"></div>
                  {{ $currency(payment.payout.amount) }}
                </template>
                <template v-else>
                  <div class="animate-pulse block h-em w-em rounded-full bg-gray-300 mr-2"></div>
                  Pending
                </template>
              </div>
            </td>
            <td><code class="text-xs">{{ payment.external_id }}</code></td>
          </tr>
        </tbody>
      </fm-table>
      <div v-if="!payments || !payments.results.length" class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-b-lg border border-t-0">
        <div class="text-sm">Member hasn't made any transactions.</div>
      </div>
      <!-- payment history table end -->

      <!-- nuxt button start -->
      <div v-if="payments && payments.next" class="text-center mt-4">
        <fm-button size="sm" :loading="isNextPaymentsLoading" @click="fetchMorePaymentsLocal(payments.next)">Load More</fm-button>
      </div>
      <!-- nuxt button end -->

      <!-- legend start -->
      <div class="inline-flex flex-col text-xs my-8">
        <div class="inline-flex items-center">
          <div class="block h-em w-em rounded-full bg-gray-300 mr-1"></div> Payout is scheduled to process.
        </div>
        <div class="inline-flex items-center mt-1">
          <div class="block h-em w-em rounded-full bg-fm-warning mr-1"></div> Payout is being processed.
        </div>
        <div class="inline-flex items-center mt-1 mr-6">
          <div class="block h-em w-em rounded-full bg-fm-success mr-1"></div> Payout was successfully sent to your bank account.
        </div>
      </div>
      <!-- legend end -->
    </template>
  </fm-dialog>
  <!-- dialogs end -->
</div>
</template>

<script>
import debounce from 'lodash/debounce';
import { mapActions, mapState } from 'vuex';

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
    title: 'Received Donations'
  },
  computed: {
    ...mapState('donations', ['donations', 'payments', 'stats']),
    hasActiveFilters() {
      return !!(this.filter.search);
    }
  },
  mounted() {
    this.loadDonations();
    this.fetchStats();
  },
  methods: {
    ...mapActions('donations', [
      'fetchReceivedDonations', 'fetchMoreDonations', 'fetchPayments', 'fetchMorePayments', 'fetchStats',
      'updateDonationMessageVisibility'
    ]),
    handleSearchInput: debounce(function() {
      this.loadDonations();
    }, 250),
    loadDonations() {
      const params = { creator_username: this.$auth.user.username, ordering: this.filter.orderBy };
      if (this.filter.search) {
        params.search = this.filter.search;
      }
      this.fetchReceivedDonations(params);
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
    },
    async toggleMessageVisibility(donation) {
      const err = await this.updateDonationMessageVisibility({ id: donation.id, payload: { is_hidden: !donation.is_hidden } });
      if (err) return;
      this.activeDonation = this.donations.results.find(currDonation => currDonation.id === donation.id);
    }
  }
};
</script>
