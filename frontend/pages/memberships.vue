<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <!-- header start -->
  <div class="container sm:pl-0">
    <div class="text-2xl text-black font-bold">
      <template v-if="$auth.user.is_creator">My</template> Memberships
    </div>
    <div class="mt-1 text-gray-600">View and manage your memberships and review transaction history.</div>
  </div>
  <!-- header end -->

  <!-- container start -->
  <div v-if="memberships" class="container mt-5 pt-6 pb-16 md:px-8 rounded-xl border bg-white">

    <!-- filters start -->
    <div class="flex flex-wrap w-full">

      <!-- search start -->
      <div class="mr-auto lg:max-w-sm flex-grow">
        <label class="text-sm block font-bold mb-2">Search for memberships</label>
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
        <fm-input v-model="filter.orderBy" type="select" @change="loadMemberships">
          <option value="-created_at">Newest membership first</option>
          <option value="created_at">Oldest membership first</option>
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
        <col class="min-w-[150px]"> <!-- tier -->
        <col class="min-w-[75px]"> <!-- active -->
        <col class="min-w-[140px]"> <!-- lifetime amount -->
        <col class="min-w-[130px]"> <!-- next renewal -->
        <col class="w-[100px]"> <!-- actions -->
      </colgroup>
      <thead>
        <tr class="text-xs uppercase">
          <th>Member</th>
          <th>Tier</th>
          <th class="!text-center">Active</th>
          <th class="!text-right">Lifetime amount</th>
          <th>Next Renewal</th>
          <th></th>
        </tr>
      </thead>
      <tbody v-show="memberships.results.length" class="text-sm">
        <tr v-for="membership in memberships.results" :key="membership.id">
          <th>
            <div class="flex items-center">
              <fm-avatar
                :src="membership.creator_user.avatar && membership.creator_user.avatar.small"
                :name="membership.creator_user.display_name"
                size="w-5 h-5 lg:w-7 lg:h-7 mr-2 inline-block font-normal flex-shrink-0">
              </fm-avatar>
              <div class="max-w-[100px] lg:max-w-[200px] font-normal">
                <div class="truncate text-xs lg:text-sm text-black" :title="membership.creator_user.display_name">{{ membership.creator_user.display_name }}</div>
                <div v-if="membership.creator_user.one_liner" class="hidden lg:block truncate text-xs font-normal text-gray-500">{{ membership.creator_user.one_liner }}</div>
              </div>
            </div>
          </th>
          <td>{{ membership.tier.name }}</td>
          <td :class="membership.is_active ? 'text-fm-success' : 'text-fm-error'" class="text-center">
            <icon-check v-if="membership.is_active" class="h-6 w-6"></icon-check>
            <icon-x v-else class="h-6 w-6"></icon-x>
          </td>
          <td class="text-right">{{ $currency(membership.lifetime_amount) }}</td>
          <td>{{ $date(membership.active_subscription.cycle_end_at) }}</td>
          <td class="text-center">
            <fm-button size="sm" @click="viewMembership(membership)">Details</fm-button>
          </td>
        </tr>
      </tbody>
    </fm-table>
    <div v-if="!memberships.results.length" class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-b-lg border border-t-0">
      <div class="text-sm">
        <template v-if="hasActiveFilters">No results matched your filtering criteria.</template>
        <!-- TODO: explore featured creators -->
        <template v-else>You don't have any memberships yet.</template>
      </div>
    </div>
    <!-- table end -->

    <!-- next button start -->
    <div v-if="memberships.next" class="text-center mt-4">
      <fm-button :loading="isNextMembershipsLoading" @click="fetchMoreMembershipsLocal(memberships.next)">Load More</fm-button>
    </div>
    <!-- next button end -->
  </div>
  <!-- container end -->

  <!-- dialogs start -->
  <fm-dialog v-model="showDialog" drawer>
    <template #header>
      <div v-if="activeMembership" class="text-base">
        Membership details for {{ activeMembership.creator_user.display_name }}
      </div>
    </template>

    <template v-if="activeMembership">
      <!-- name, one liner and avatar start -->
      <div class="flex items-center">
        <fm-avatar
          :src="activeMembership.creator_user.avatar && activeMembership.creator_user.avatar.small"
          :name="activeMembership.creator_user.display_name"
          size="w-8 h-8 mr-2 inline-block font-normal flex-shrink-0">
        </fm-avatar>
        <div>
          <div class="text-black" :title="activeMembership.creator_user.display_name">{{ activeMembership.creator_user.display_name }}</div>
          <div v-if="activeMembership.creator_user.one_liner" class="text-xs font-normal text-gray-500">
            {{ activeMembership.creator_user.one_liner }}
          </div>
        </div>
      </div>
      <!-- name, one liner and avatar end -->

      <hr class="my-4">

      <!-- key value pairs start -->
      <dl>

        <!-- status and cancel membership start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Status</dt>
          <dd class="flex items-center flex-grow flex-wrap">
            <div class="font-medium mr-auto" :class="{
              'text-fm-success-600': activeMembership.status === 'active',
              'text-fm-error': activeMembership.status !== 'active'
            }">
              {{ STATUS_TEXT_MAP[activeMembership.status] }}
            </div>
            <fm-button
              v-if="activeMembership.status == 'active'" type="error" size="sm" class="flex items-center"
              @click="cancelMembershipLocal(activeMembership.id)">
              <icon-slash class="h-em w-em mr-1"></icon-slash>
              Cancel membership
            </fm-button>
          </dd>
        </div>
        <!-- status and cancel membership end -->

        <!-- tier name start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Tier</dt>
          <dd class="flex-grow">{{ activeMembership.tier.name }}</dd>
        </div>
        <!-- tier name end -->

        <!-- next renewal start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Next renewal</dt>
          <dd class="flex-grow">{{ $datetime(activeMembership.active_subscription.cycle_end_at) }}</dd>
        </div>
        <!-- next renewal end -->

        <!-- next tier start -->
        <div
          v-if="activeMembership.scheduled_subscription && activeMembership.scheduled_subscription.status == 'scheduled_to_activate'"
          class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Next tier</dt>
          <dd class="flex-grow">{{ activeMembership.scheduled_subscription.tier.name }}</dd>
        </div>
        <!-- next tier end -->

        <!-- lifetime amount start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Lifetime amount</dt>
          <dd class="flex-grow">{{ $currency(activeMembership.lifetime_amount) }}</dd>
        </div>
        <!-- lifetime amount end -->

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
        <div class="text-sm">You haven't made any transactions towards this membership.</div>
      </div>
      <!-- payment history table end -->

      <!-- next button start -->
      <div v-if="payments && payments.next" class="text-center mt-4">
        <fm-button size="sm" :loading="isNextPaymentsLoading" @click="fetchMorePaymentsLocal(payments.next)">Load More</fm-button>
      </div>
      <!-- next button end -->

      <div class="my-8"></div>
    </template>
  </fm-dialog>
  <!-- dialogs end -->
</div>
</template>

<script>
import debounce from 'lodash/debounce';
import { mapActions, mapState } from 'vuex';
import { STATUS_TEXT_MAP } from '~/utils';

export default {
  layout: 'with-sidebar',
  data() {
    return {
      STATUS_TEXT_MAP,
      filter: {
        search: '',
        orderBy: '-created_at'
      },
      showDialog: false,
      activeMembership: null,
      isNextMembershipsLoading: false,
      isNextPaymentsLoading: false
    };
  },
  head: {
    title: 'Memberships'
  },
  computed: {
    ...mapState('memberships', ['memberships', 'payments']),
    hasActiveFilters() {
      return !!(this.filter.search);
    }
  },
  mounted() {
    this.loadMemberships();
  },
  methods: {
    ...mapActions('memberships', ['fetchMemberships', 'fetchMoreMemberships', 'fetchPayments', 'fetchMorePayments', 'cancelMembership']),
    loadMemberships() {
      const params = { fan_username: this.$auth.user.username, ordering: this.filter.orderBy };
      if (this.filter.search) {
        params.search = this.filter.search;
      }
      this.fetchMemberships(params);
    },
    viewMembership(membership) {
      this.activeMembership = membership;
      this.showDialog = true;
      this.fetchPayments(membership.id);
    },
    handleSearchInput: debounce(function() {
      this.loadMemberships();
    }, 250),
    async cancelMembershipLocal(userId) {
      try {
        await this.$confirm.error('This will schedule the membership to cancel on next renewal date. Are you sure you want cancel this membership?', 'Cancel membership');
      } catch (err) {
        return;
      }
      this.cancelMembership(userId);
    },
    async fetchMoreMembershipsLocal(url) {
      this.isNextMembershipsLoading = true;
      await this.fetchMoreMembers(url);
      this.isNextMembershipsLoading = false;
    },
    async fetchMorePaymentsLocal(url) {
      this.isNextPaymentsLoading = true;
      await this.fetchMorePayments(url);
      this.isNextPaymentsLoading = false;
    }
  }
};
</script>
