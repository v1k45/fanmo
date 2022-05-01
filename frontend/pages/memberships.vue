<template>
<div v-if="memberships != null">
  <div>
    <div class="mt-8 flex max-w-md">
      <div class="flex-grow mr-2"><fm-input v-model="filter.search" placeholder="Search by name or email"></fm-input></div>
      <div><fm-button type="primary" @click="loadMemberships">Search</fm-button></div>
    </div>
    <div class="mt-8 flex max-w-md items-center">
      <div class="flex-grow mr-2">
        <fm-input v-model="filter.isActive" type="select" label="Active Status">
          <option value="null">All</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </fm-input>
      </div>
      <div><fm-button type="primary" @click="loadMemberships">Filter</fm-button></div>
    </div>
    <div class="mt-8 flex max-w-md items-center">
      <div class="flex-grow mr-2">
        <fm-input v-model="filter.orderBy" type="select" label="Sort by">
          <option value="-created_at">Newest first</option>
          <option value="created_at">Oldest first</option>
          <option value="-lifetime_amount">Highest lifetime amount first</option>
          <option value="lifetime_amount">Lowest lifetime amount first</option>
        </fm-input>
      </div>
      <div><fm-button type="primary" @click="loadMemberships">Sort</fm-button></div>
    </div>
  </div>
  <table class="table table-auto">
    <thead>
      <tr>
        <th>Member</th>
        <th>Tier</th>
        <th>Active</th>
        <th>Lifetime amount</th>
        <th>Next Renewal</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="membership in memberships.results" :key="membership.id">
        <td>{{ membership.creator_user.display_name }}</td>
        <td>{{ membership.tier.name }}</td>
        <td>{{ membership.is_active }}</td>
        <td>{{ membership.lifetime_amount }}</td>
        <td>{{ membership.active_subscription.cycle_end_at }}</td>
        <td><fm-button type="info" @click="viewMembership(membership)">view</fm-button></td>
      </tr>
    </tbody>
  </table>
  <fm-button v-if="memberships.next" type="info" @click="fetchMoreMemberships(memberships.next)">Load More</fm-button>
  <fm-dialog v-if="activeMembership" v-model="showDialog">
    <template #header>{{ activeMembership.creator_user.display_name }}</template>
    <dl>
      <dt>Status</dt>
      <dd>
        {{ activeMembership.status }}
        <fm-button v-if="activeMembership.status == 'active'" type="error" @click="cancelMembership(activeMembership.id)">cancel</fm-button>
      </dd>
      <dt>Tier</dt>
      <dd>{{ activeMembership.tier.name }}</dd>
      <dt>Next renewal</dt>
      <dd>{{ activeMembership.active_subscription.cycle_end_at }}</dd>
      <template v-if="activeMembership.scheduled_subscription && activeMembership.scheduled_subscription.status == 'scheduled_to_activate'">
        <dt>Next Tier</dt>
        <dd>{{ activeMembership.scheduled_subscription.tier.name }}</dd>
      </template>
      <dt>Lifetime amount</dt>
      <dd>{{ activeMembership.lifetime_amount }}</dd>
    </dl>
    <h3>Payment History</h3>
    <table v-if="payments" class="table table-auto">
      <thead>
        <tr>
          <td>Date</td>
          <td>Amount</td>
          <td>Transaction ID</td>
          <td>Payout</td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="payment in payments.results" :key="payment.id">
          <td>{{ payment.created_at }}</td>
          <td>{{ payment.amount }}</td>
          <td>{{ payment.external_id }}</td>
          <td v-if="payment.payout">{{ payment.payout.amount }} {{ payment.payout.status }}</td>
          <td v-else>Pending</td>
        </tr>
      </tbody>
    </table>
    <fm-button v-if="payments && payments.next" type="info" @click="fetchMorePayments(payments.next)">Load More</fm-button>
  </fm-dialog>
</div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  layout: 'with-sidebar',
  data() {
    return {
      filter: {
        search: '',
        isActive: null,
        orderBy: '-created_at'
      },
      showDialog: true,
      activeMembership: null
    };
  },
  head: {
    title: 'Memberships'
  },
  computed: {
    ...mapState('memberships', ['memberships', 'payments'])
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
      if (this.filter.isActive != null) {
        params.is_active = this.filter.isActive;
      }
      this.fetchMemberships(params);
    },
    viewMembership(membership) {
      this.activeMembership = membership;
      this.showDialog = true;
      this.fetchPayments(membership.id);
    }
  }
};
</script>
