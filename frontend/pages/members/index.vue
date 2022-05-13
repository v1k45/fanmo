<template>
<div v-if="members">
  <!-- stats start -->
  <div v-if="stats" class="flex flex-wrap text-center mb-6">
    <div>
      <div class="text-lg sm:text-3xl font-bold">{{ stats.total }}</div>
      <div class="text-xs sm:text-sm text-gray-600">total members</div>
    </div>
    <div class="ml-3 sm:ml-10">
      <div class="text-lg sm:text-3xl font-bold">{{ stats.active }}</div>
      <div class="text-xs sm:text-sm text-gray-600">active members</div>
    </div>
    <div class="ml-3 sm:ml-10">
      <div class="text-lg sm:text-3xl font-bold">{{ stats.inactive }}</div>
      <div class="text-xs sm:text-sm text-gray-600">inactive members</div>
    </div>
    <div class="ml-3 sm:ml-10">
      <div class="text-lg sm:text-3xl font-bold">{{ $currency(stats.total_payment) }}</div>
      <div class="text-xs sm:text-sm text-gray-600">total payment</div>
    </div>

    <div class="lg:block xl:hidden w-full mb-4"></div>
    <div class="ml-auto">
      <fm-button class="flex" type="primary" @click="dialogs.giveaway = true">
        <icon-gift class="w-4 h-4 mr-2"></icon-gift> Gift memberships
      </fm-button>
    </div>
  </div>
  <!-- stats end -->

  <!-- filters start -->
  <div class="flex flex-wrap w-full">

    <!-- search start -->
    <div class="mr-auto lg:max-w-sm flex-grow">
      <label class="text-sm block font-bold mb-2">Search for users</label>
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
      <fm-input v-model="filter.orderBy" type="select" @change="loadMemberships">
        <option value="-created_at">Newest member first</option>
        <option value="created_at">Oldest member first</option>
        <option value="-lifetime_amount">Highest lifetime amount first</option>
        <option value="lifetime_amount">Lowest lifetime amount first</option>
      </fm-input>
    </div>
    <!-- sort end -->

    <!-- active filter start -->
    <div class="flex-grow sm:flex-grow-0">
      <label class="text-sm block font-bold mb-2">Active status</label>
      <fm-input v-model="filter.isActive" type="select" @change="loadMemberships">
        <option :value="null">All</option>
        <option :value="true">Active</option>
        <option :value="false">Inactive</option>
      </fm-input>
    </div>
    <!-- active filter end -->

  </div>
  <!-- filters end -->

  <!-- table start -->
  <fm-table class="mt-8 table-fixed lg:table-auto" first-column-sticky>
    <colgroup>
      <col class="w-[100px] md:min-w-[200px]"> <!-- member -->
      <col class="min-w-[140px]"> <!-- lifetime amount -->
      <col class="min-w-[150px]"> <!-- tier -->
      <col class="min-w-[75px]"> <!-- active -->
      <col class="min-w-[130px]"> <!-- next renewal -->
      <col class="w-[100px]"> <!-- actions -->
    </colgroup>
    <thead>
      <tr class="text-xs uppercase">
        <th>Member</th>
        <th class="!text-right">Lifetime amount</th>
        <th>Tier</th>
        <th class="!text-center">Active</th>
        <th>Next Renewal</th>
        <th></th>
      </tr>
    </thead>
    <tbody v-show="members.results.length" class="text-sm">
      <tr v-for="member in members.results" :key="member.id">
        <th>
          <div class="flex items-center">
            <fm-avatar
              :src="member.fan_user.avatar && member.fan_user.avatar.small"
              :name="member.fan_user.display_name" :username="member.fan_user.username"
              size="w-5 h-5 lg:w-7 lg:h-7 mr-2 inline-block font-normal flex-shrink-0">
            </fm-avatar>
            <div class="max-w-[100px] lg:max-w-[200px] font-normal">
              <div class="truncate text-xs lg:text-sm text-black" :title="member.fan_user.display_name">{{ member.fan_user.display_name }}</div>
              <div class="truncate text-xs font-normal text-gray-500">
                <a class="unstyled" :href="`mailto:${member.fan_user.email}`">{{ member.fan_user.email }}</a>
              </div>
            </div>
          </div>
        </th>
        <td class="text-right">{{ $currency(member.lifetime_amount) }}</td>
        <td>{{ member.tier.name }}</td>
        <td :class="member.is_active ? 'text-fm-success' : 'text-fm-error'" class="text-center">
          <icon-check v-if="member.is_active" class="h-6 w-6"></icon-check>
          <icon-x v-else class="h-6 w-6"></icon-x>
        </td>
        <td>{{ $date(member.active_subscription.cycle_end_at) }}</td>
        <td class="text-center">
          <fm-button size="sm" @click="viewMember(member)">Details</fm-button>
        </td>
      </tr>
    </tbody>
  </fm-table>
  <div v-if="!members.results.length" class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-b-lg border border-t-0">
    <div class="text-sm">
      <template v-if="hasActiveFilters">No results matched your filtering criteria.</template>
      <template v-else>You don't have any members yet.</template>
    </div>
  </div>
  <!-- table end -->

  <!-- next button start -->
  <div v-if="members.next" class="text-center mt-4">
    <fm-button :loading="isNextMembersLoading" @click="fetchMoreMembersLocal(members.next)">Load More</fm-button>
  </div>
  <!-- next button end -->



  <!-- dialogs start -->
  <fm-dialog v-model="dialogs.detail" drawer>
    <template #header>
      <div v-if="activeMember" class="text-base">
        Membership details for {{ activeMember.fan_user.display_name }}
      </div>
    </template>

    <template v-if="activeMember">
      <!-- name, email and avatar start -->
      <div class="flex items-center">
        <fm-avatar
          :src="activeMember.fan_user.avatar && activeMember.fan_user.avatar.small"
          :name="activeMember.fan_user.display_name" :username="activeMember.fan_user.username"
          size="w-8 h-8 mr-2 inline-block font-normal flex-shrink-0">
        </fm-avatar>
        <div>
          <div class="truncate text-black" :title="activeMember.fan_user.display_name">{{ activeMember.fan_user.display_name }}</div>
          <div class="truncate text-xs font-normal text-gray-500">
            <a class="unstyled" :href="`mailto:${activeMember.fan_user.email}`">{{ activeMember.fan_user.email }}</a>
          </div>
        </div>
      </div>
      <!-- name, email and avatar end -->

      <hr class="my-4">

      <!-- key value pairs start -->
      <dl>

        <!-- status and cancel membership start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Status</dt>
          <dd class="flex items-center flex-grow flex-wrap">
            <div class="font-medium mr-auto" :class="{
              'text-fm-success-600': activeMember.status === 'active',
              'text-fm-error': activeMember.status !== 'active'
            }">
              {{ STATUS_TEXT_MAP[activeMember.status] }}
            </div>
            <fm-button
              v-if="activeMember.status == 'active'" type="error" size="sm" class="flex items-center"
              @click="cancelMembershipLocal(activeMember.id)">
              <icon-slash class="h-em w-em mr-1"></icon-slash>
              Cancel membership
            </fm-button>
          </dd>
        </div>
        <!-- status and cancel membership end -->

        <!-- tier name start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Tier</dt>
          <dd class="flex-grow">{{ activeMember.tier.name }}</dd>
        </div>
        <!-- tier name end -->

        <!-- next renewal start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Next renewal</dt>
          <dd class="flex-grow">{{ $datetime(activeMember.active_subscription.cycle_end_at) }}</dd>
        </div>
        <!-- next renewal end -->

        <!-- next tier start -->
        <div
          v-if="activeMember.scheduled_subscription && activeMember.scheduled_subscription.status == 'scheduled_to_activate'"
          class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Next tier</dt>
          <dd class="flex-grow">{{ activeMember.scheduled_subscription.tier.name }}</dd>
        </div>
        <!-- next tier end -->

        <!-- lifetime amount start -->
        <div class="flex items-baseline mb-2">
          <dt class="text-sm text-gray-500 w-1/3 mr-2 md:w-1/4">Lifetime amount</dt>
          <dd class="flex-grow">{{ $currency(activeMember.lifetime_amount) }}</dd>
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
                  <div v-if="payment.payout.status === 'scheduled'" class="animate-pulse block h-em w-em rounded-full bg-fm-warning mr-2"></div>
                  <div v-else-if="payment.payout.status === 'processed'" class="block h-em w-em rounded-full bg-fm-success mr-2"></div>
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

  <fm-dialog v-model="dialogs.giveaway">
    <template #header>
      <div class="flex items-center">
        <icon-gift class="text-fm-primary h-8 w-8 mt-0 mr-2"></icon-gift>
        <div>
          Gift memberships

          <div class="text-sm text-gray-600 font-normal">Gift a 1 month free membership to your fans</div>
        </div>
      </div>
    </template>

    <fm-form
      v-for="(giveaway, idx) in giveawayForm" :key="idx" :errors="giveawayFormErrors[idx]"
      class="flex space-x-3 mb-6" @submit.prevent>
      <div class="flex-1">
        <fm-input v-model="giveaway.email" uid="email" label="Email" required type="email" placeholder="name@example.com"></fm-input>
      </div>
      <div class="flex-1">
        <fm-input v-model="giveaway.tier_id" uid="tier_id" label="Tier" type="select" required>
          <option v-for="tier in $auth.user.tiers" :key="tier.id" :value="tier.id">{{ tier.name }}</option>
        </fm-input>
      </div>
      <div v-if="giveawayForm.length > 1" class="self-end mb-2">
        <fm-button size="sm" circle @click="addOrRemoveGiveawayForm(idx)">
          <icon-x class="w-4 h-4 text-fm-error"></icon-x>
        </fm-button>
      </div>
    </fm-form>
    <div class="text-right mb-3">
      <fm-button size="sm" @click="addOrRemoveGiveawayForm">Add another</fm-button>
    </div>
    <template #footer>
      <div class="text-right">
        <fm-button @click="dialogs.giveaway = false;">Cancel</fm-button>
        <fm-button type="primary" @click="submitGiveaway">Send invites</fm-button>
      </div>
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
  data() {
    return {
      STATUS_TEXT_MAP,
      filter: {
        search: '',
        isActive: null,
        orderBy: '-created_at'
      },
      giveawayForm: [
        { tier_id: '', email: '' }
      ],
      giveawayFormErrors: [],
      dialogs: {
        detail: false,
        giveaway: false
      },
      activeMember: null,
      isNextMembersLoading: false,
      isNextPaymentsLoading: false
    };
  },
  head: {
    title: 'Members'
  },
  computed: {
    ...mapState('memberships', ['members', 'payments', 'stats']),
    hasActiveFilters() {
      return !!(this.filter.search || this.filter.isActive !== null);
    }
  },
  mounted() {
    this.loadMemberships();
    this.fetchStats();
  },
  methods: {
    ...mapActions('memberships', [
      'fetchMembers', 'fetchMoreMembers', 'fetchPayments', 'fetchMorePayments', 'cancelMembership', 'fetchStats', 'giveawayMembership'
    ]),
    loadMemberships() {
      const params = { creator_username: this.$auth.user.username, ordering: this.filter.orderBy };
      if (this.filter.search) {
        params.search = this.filter.search;
      }
      if (this.filter.isActive !== null) {
        params.is_active = this.filter.isActive;
      }
      this.fetchMembers(params);
    },
    handleSearchInput: debounce(function() {
      this.loadMemberships();
    }, 250),
    viewMember(member) {
      this.activeMember = member;
      this.dialogs.detail = true;
      this.fetchPayments(member.id);
    },
    async cancelMembershipLocal(userId) {
      try {
        await this.$confirm.error('This will schedule the membership to cancel on next renewal date. Are you sure you want cancel this membership?', 'Cancel membership');
      } catch (err) {
        return;
      }
      this.cancelMembership(userId);
    },
    async fetchMoreMembersLocal(url) {
      this.isNextMembersLoading = true;
      await this.fetchMoreMembers(url);
      this.isNextMembersLoading = false;
    },
    async fetchMorePaymentsLocal(url) {
      this.isNextPaymentsLoading = true;
      await this.fetchMorePayments(url);
      this.isNextPaymentsLoading = false;
    },
    addOrRemoveGiveawayForm(idx = null) {
      if (Number.isInteger(idx)) {
        this.giveawayForm.splice(idx, 1);
      } else {
        this.giveawayForm.push({ tier_id: '', email: '' });
      }
    },
    async submitGiveaway() {
      const error = await this.giveawayMembership(this.giveawayForm);
      if (error) {
        this.giveawayFormErrors = error;
        this.loading = false;
        return;
      }
      this.$toast.success('Membership invitations were sent successfully.');
      this.dialogs.giveaway = false;
      this.giveawayForm = [{ tier_id: '', email: '' }];
      this.loadMemberships();
    }
  }
};
</script>
