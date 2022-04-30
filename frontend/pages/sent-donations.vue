<template>
<div v-if="donations != null">
  <div>
    <div class="mt-8 flex max-w-md">
      <div class="flex-grow mr-2"><fm-input v-model="filter.search" placeholder="Search by name or email"></fm-input></div>
      <div><fm-button type="primary" @click="loadDonations">Search</fm-button></div>
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
      <div><fm-button type="primary" @click="loadDonations">Sort</fm-button></div>
    </div>
  </div>
  <table class="table table-auto">
    <thead>
      <tr>
        <th>Creator</th>
        <th>Amount</th>
        <th>Message</th>
        <th>Lifetime amount</th>
        <th>Date</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="donation in donations.results" :key="donation.id">
        <td>{{ donation.creator_user.display_name }}</td>
        <td>{{ donation.amount }}</td>
        <td class="truncate">{{ donation.message }}</td>
        <td>{{ donation.lifetime_amount }}</td>
        <td>{{ donation.created_at }}</td>
        <td><fm-button type="info" @click="viewDonation(donation)">view</fm-button></td>
      </tr>
    </tbody>
  </table>
  <fm-button v-if="donations.next" type="info" @click="fetchMoreDonations(donations.next)">Load More</fm-button>
  <fm-dialog v-if="activeDonation" v-model="showDialog">
    <template #header>{{ activeDonation.creator_user.display_name }}</template>
    <dl>
      <dt>Amount</dt>
      <dd>
        {{ activeDonation.amount }}
      </dd>
      <dt>Message</dt>
      <dd>{{ activeDonation.message }}</dd>
      <dt>Date</dt>
      <dd>{{ activeDonation.created_at }}</dd>
      <dt>Lifetime amount</dt>
      <dd>{{ activeDonation.lifetime_amount }}</dd>
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
        orderBy: '-created_at'
      },
      showDialog: true,
      activeDonation: null
    };
  },
  head: {
    title: 'Received Donations'
  },
  computed: {
    ...mapState('donations', ['donations', 'payments'])
  },
  mounted() {
    this.loadDonations();
  },
  methods: {
    ...mapActions('donations', ['fetchSentDonations', 'fetchMoreDonations', 'fetchPayments', 'fetchMorePayments']),
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
    }
  }
};
</script>
