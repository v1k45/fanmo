<template>
<div v-if="earnings != null">
  <div>
    <div class="mt-8 flex max-w-md">
      <div class="flex-grow mr-2"><fm-input v-model="filter.search" placeholder="Search by name or email"></fm-input></div>
      <div><fm-button type="primary" @click="loadEarnings">Search</fm-button></div>
    </div>
    <div class="mt-8 flex max-w-md items-center">
      <div class="flex-grow mr-2">
        <fm-input v-model="filter.type" type="select" label="Active Status">
          <option value="">All</option>
          <option value="donation">Donations</option>
          <option value="subscription">Memberships</option>
        </fm-input>
      </div>
      <div><fm-button type="primary" @click="loadEarnings">Filter</fm-button></div>
    </div>
    <div class="mt-8 flex max-w-md items-center">
      <div class="flex-grow mr-2">
        <fm-input v-model="filter.orderBy" type="select" label="Sort by">
          <option value="-created_at">Newest first</option>
          <option value="created_at">Oldest first</option>
          <option value="-amount">Highest amount first</option>
          <option value="amount">Lowest amount first</option>
        </fm-input>
      </div>
      <div><fm-button type="primary" @click="loadEarnings">Sort</fm-button></div>
    </div>
  </div>
  <table class="table table-auto">
    <thead>
      <tr>
        <th>Date</th>
        <th>Amount</th>
        <th>Supporter</th>
        <th>Payout</th>
        <th>Type</th>
        <th>TXN#</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="earning in earnings.results" :key="earning.id">
        <td>{{ earning.created_at }}</td>
        <td>{{ earning.amount }}</td>
        <td>{{ earning.fan_user.display_name }}</td>
        <td v-if="earning.payout">{{ earning.payout.amount }} {{ earning.payout.status }}</td>
        <td v-else>Pending</td>
        <td>{{ earning.type }}</td>
        <td>{{ earning.external_id }}</td>
      </tr>
    </tbody>
  </table>
  <fm-button v-if="earnings.next" type="info" @click="fetchMoreEarnings(earnings.next)">Load More</fm-button>
</div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  data() {
    return {
      filter: {
        search: '',
        type: '',
        orderBy: '-created_at'
      }
    };
  },
  head: {
    title: 'Earnings'
  },
  computed: {
    ...mapState('payments', { earnings: 'payments' })
  },
  mounted() {
    this.loadEarnings();
  },
  methods: {
    ...mapActions('payments', {
      fetchEarnings: 'fetchPayments',
      fetchMoreEarnings: 'fetchMorePayments'
    }),
    loadEarnings() {
      const params = { creator_username: this.$auth.user.username, ordering: this.filter.orderBy };
      if (this.filter.search) {
        params.search = this.filter.search;
      }
      if (this.filter.type) {
        params.type = this.filter.type;
      }
      this.fetchEarnings(params);
    }
  }
};
</script>
