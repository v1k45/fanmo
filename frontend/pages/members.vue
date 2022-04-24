<template>
<div v-if="members != null">
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
      <tr v-for="member in members.results" :key="member.id">
        <td>{{ member.fan_user.display_name }}</td>
        <td>{{ member.tier.name }}</td>
        <td>{{ member.is_active }}</td>
        <td>{{ member.lifetime_amount }}</td>
        <td>{{ member.active_subscription.cycle_end_at }}</td>
        <td><fm-button type="info" @click="viewMember(member)">view</fm-button></td>
      </tr>
    </tbody>
  </table>
  <fm-button v-if="members.next" type="info" @click="fetchMoreMembers(members.next)">Load More</fm-button>
  <fm-dialog v-if="activeMember" v-model="showDialog">
    <template #header>{{ activeMember.fan_user.display_name }}</template>
    <dl>
      <dt>Status</dt>
      <dd>
        {{ activeMember.status }}
        <fm-button v-if="activeMember.status == 'active'" type="error" @click="cancelMembership(activeMember.id)">cancel</fm-button>
      </dd>
      <dt>Tier</dt>
      <dd>{{ activeMember.tier.name }}</dd>
      <dt>Next renewal</dt>
      <dd>{{ activeMember.active_subscription.cycle_end_at }}</dd>
      <template v-if="activeMember.scheduled_subscription && activeMember.scheduled_subscription.status == 'scheduled_to_activate'">
        <dt>Next Tier</dt>
        <dd>{{ activeMember.scheduled_subscription.tier.name }}</dd>
      </template>
      <dt>Lifetime amount</dt>
      <dd>{{ activeMember.lifetime_amount }}</dd>
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
  data() {
    return {
      filter: {
        search: '',
        isActive: null,
        orderBy: '-created_at'
      },
      showDialog: true,
      activeMember: null
    };
  },
  head: {
    title: 'Members'
  },
  computed: {
    ...mapState('memberships', ['members', 'payments'])
  },
  mounted() {
    this.loadMemberships();
  },
  methods: {
    ...mapActions('memberships', ['fetchMembers', 'fetchMoreMembers', 'fetchPayments', 'fetchMorePayments', 'cancelMembership']),
    loadMemberships() {
      const params = { creator_username: this.$auth.user.username, ordering: this.filter.orderBy };
      if (this.filter.search) {
        params.search = this.filter.search;
      }
      if (this.filter.isActive != null) {
        params.is_active = this.filter.isActive;
      }
      this.fetchMembers(params);
    },
    viewMember(member) {
      this.activeMember = member;
      this.showDialog = true;
      this.fetchPayments(member.id);
    }
  }
};
</script>
