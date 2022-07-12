<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <!-- header start -->
  <div class="container sm:pl-0">
    <div class="text-2xl text-black font-bold">Earnings</div>
    <!-- TODO: change -->
    <div class="mt-1 text-gray-600">View your earnings and stats.</div>
  </div>
  <!-- header end -->

  <!-- container start -->
  <div v-if="earnings" class="container mt-5 pt-3 pb-16 md:px-8 rounded-xl border bg-white">

    <div v-if="stats" class="flex xl:space-x-12 flex-wrap mb-6">
      <div class="w-1/2 sm:w-1/3 xl:w-[unset] mt-3 text-sm md:text-base">
        <div class="text-gray-500">Total transactions</div>
        <div class="flex items-end">
          <div class="text-lg md:text-xl font-medium">{{ stats.total }}</div>
        </div>
      </div>
      <div class="w-1/2 sm:w-1/3 xl:w-[unset] mt-3 text-sm md:text-base">
        <div class="text-gray-500">Total earnings</div>
        <div class="flex items-end">
          <div class="text-lg md:text-xl font-medium">{{ $currency(stats.total_amount || 0) }}</div>
        </div>
      </div>
      <div class="w-1/2 sm:w-1/3 xl:w-[unset] mt-3 text-sm md:text-base">
        <div class="text-gray-500">Payout processed</div>
        <div class="flex items-end">
          <div class="text-lg md:text-xl font-medium">{{ $currency(stats.total_payout_processed || 0) }}</div>
        </div>
      </div>
      <div class="w-1/2 sm:w-1/3 xl:w-[unset] mt-3 text-sm md:text-base">
        <div class="text-gray-500">Payout scheduled</div>
        <div class="flex items-end">
          <div class="text-lg md:text-xl font-medium">{{ $currency(stats.total_payout_scheduled || 0) }}</div>
        </div>
      </div>
      <div class="lg:block xl:hidden w-full mb-2"></div>
      <div class="xl:!ml-auto">
        <fm-button class="flex mt-3" @click="exportCSV">
          <icon-download class="w-4 h-4 mr-2"></icon-download> Download CSV
        </fm-button>
      </div>
    </div>

    <!-- filters start -->
    <div class="flex flex-wrap w-full">

      <!-- search start -->
      <div class="mr-auto lg:max-w-sm flex-grow">
        <label class="text-sm block font-bold mb-2">Search for payments</label>
        <!-- TODO: placeholder -->
        <fm-input v-model="filter.search" placeholder="Search by name or email" @input="handleSearchInput">
          <template #prepend>
            <icon-search class="w-em"></icon-search>
          </template>
        </fm-input>
      </div>
      <!-- search end -->

      <div class="w-full mt-4 lg:hidden"></div>

      <!-- sort start -->
      <div class="w-2/4 sm:w-[unset] lg:ml-4 mr-4">
        <label class="text-sm block font-bold mb-2">Sort by</label>
        <fm-input v-model="filter.orderBy" type="select" @change="loadEarnings">
          <option value="-created_at">Newest first</option>
          <option value="created_at">Oldest first</option>
          <option value="-amount">Highest amount first</option>
          <option value="amount">Lowest amount first</option>
        </fm-input>
      </div>
      <!-- sort end -->

      <!-- payment type filter start -->
      <div class="flex-grow sm:flex-grow-0">
        <label class="text-sm block font-bold mb-2">Payment type</label>
        <fm-input v-model="filter.type" type="select" @change="loadEarnings">
          <option value="">All</option>
          <option value="donation">Donation</option>
          <option value="subscription">Membership</option>
        </fm-input>
      </div>
      <!-- payment type filter end -->

    </div>
    <!-- filters end -->

    <!-- table start -->
    <fm-table class="mt-8 table-fixed lg:table-auto">
      <colgroup>
        <col class="w-[100px] md:min-w-[200px]"> <!-- supporter -->
        <col class="min-w-[175px]"> <!-- next renewal -->
        <col class="min-w-[100px]"> <!-- amount -->
        <col> <!-- payout -->
        <col> <!-- type -->
        <col> <!-- method -->
        <col> <!-- txn id -->
      </colgroup>
      <thead>
        <tr class="text-xs uppercase">
          <th>Supporter</th>
          <th>Date</th>
          <th class="!text-right">Amount</th>
          <th>Payout</th>
          <th>Type</th>
          <th>Method</th>
          <th>Transaction ID</th>
        </tr>
      </thead>
      <tbody v-show="earnings.results.length" class="text-sm">
        <tr v-for="earning in earnings.results" :key="earning.id">

          <td>
            <div class="flex items-center">
              <fm-avatar
                :src="earning.fan_user.avatar && earning.fan_user.avatar.small"
                :name="earning.fan_user.display_name" :username="earning.fan_user.username"
                size="w-5 h-5 lg:w-7 lg:h-7 mr-2 inline-block font-normal flex-shrink-0">
              </fm-avatar>
              <div class="max-w-[100px] lg:max-w-[200px] font-normal">
                <div class="truncate text-xs lg:text-sm text-black" :title="earning.fan_user.display_name">{{ earning.fan_user.display_name }}</div>
                <div class="truncate text-xs font-normal text-gray-500">
                  <a class="unstyled" :href="`mailto:${earning.fan_user.email}`">{{ earning.fan_user.email }}</a>
                </div>
              </div>
            </div>
          </td>
          <td><span class="whitespace-nowrap">{{ $datetime(earning.created_at) }}</span></td>
          <td class="text-right">{{ $currency(earning.amount) }}</td>
          <td>
            <div class="flex items-center">
              <template v-if="earning.payout">
                <div v-if="earning.payout.status === 'scheduled'" class="animate-pulse block h-em w-em rounded-full bg-gray-300 mr-2"></div>
                <div v-else-if="earning.payout.status === 'processed'" class="block h-em w-em rounded-full bg-fm-warning mr-2"></div>
                <div v-else-if="earning.payout.status === 'settled'" class="block h-em w-em rounded-full bg-fm-success mr-2"></div>
                {{ $currency(earning.payout.amount) }}
              </template>
              <template v-else>
                <div class="animate-pulse block h-em w-em rounded-full bg-gray-300 mr-2"></div>
                Pending
              </template>
            </div>
          </td>
          <td>{{ earning.type === 'subscription' ? 'Membership' : 'Donation' }}</td>
          <td>{{ METHOD_NAME_MAP[earning.method] || earning.method }}</td>
          <td><code class="text-xs">{{ earning.external_id }}</code></td>
        </tr>
      </tbody>
    </fm-table>
    <div v-if="!earnings.results.length" class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-b-lg border border-t-0">
      <div class="text-sm">
        <template v-if="hasActiveFilters">No results matched your filtering criteria.</template>
        <template v-else>You haven't received any payments yet.</template>
      </div>
    </div>
    <!-- table end -->

    <!-- next button start -->
    <div v-if="earnings.next" class="text-center mt-4">
      <fm-button :loading="isNextEarningsLoading" @click="fetchMoreEarningsLocal(earnings.next)">Load More</fm-button>
    </div>
    <!-- next button end -->

    <!-- legend start -->
    <div class="inline-flex flex-col text-xs mt-8">
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

  </div>
  <!-- container end -->

</div>
</template>

<script>
import debounce from 'lodash/debounce';
import { mapActions, mapState } from 'vuex';

const METHOD_NAME_MAP = {
  card: 'Card',
  netbanking: 'Net Banking',
  upi: 'UPI',
  wallet: 'Wallet',
  giveaway: 'Giveaway'
};

export default {
  layout: 'with-sidebar',
  data() {
    return {
      METHOD_NAME_MAP,
      filter: {
        search: '',
        type: '',
        orderBy: '-created_at'
      },
      isNextEarningsLoading: false
    };
  },
  head: {
    title: 'Earnings'
  },
  computed: {
    ...mapState('payments', { earnings: 'payments', stats: 'stats' }),
    hasActiveFilters() {
      return !!(this.filter.search || this.filter.type);
    }
  },
  mounted() {
    this.loadEarnings();
    this.fetchStats();
  },
  methods: {
    ...mapActions('payments', {
      fetchEarnings: 'fetchPayments',
      fetchMoreEarnings: 'fetchMorePayments',
      fetchStats: 'fetchStats'
    }),
    exportCSV() {
      window.location.href = '/api/payments/export/';
    },
    loadEarnings() {
      const params = { creator_username: this.$auth.user.username, ordering: this.filter.orderBy };
      if (this.filter.search) {
        params.search = this.filter.search;
      }
      if (this.filter.type) {
        params.type = this.filter.type;
      }
      this.fetchEarnings(params);
    },
    handleSearchInput: debounce(function() {
      this.loadEarnings();
    }, 250),
    async fetchMoreEarningsLocal(url) {
      this.isNextEarningsLoading = true;
      await this.fetchMoreEarnings(url);
      this.isNextEarningsLoading = false;
    }
  }
};
</script>
