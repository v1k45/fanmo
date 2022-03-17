<template>
<div>
  <h1 class="text-2xl font-bold">Payments <span v-if="payments.count">({{ payments.count }})</span></h1>
  <div class="mt-2 font-medium opacity-70">View your payments</div>

  <div class="form-control mt-6">
    <input type="text" placeholder="Search payments" class="input input-bordered">
  </div>
  <div v-if="payments.results.length" class="overflow-x-auto mt-6 border rounded-lg">
    <table class="table table-zebra w-full">
      <thead>
        <tr>
          <th>Creator</th>
          <th align="center">Type</th>
          <th>Amount</th>
          <th>Paid on</th>
          <th align="center">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="payment in payments.results" :key="payment.id">
          <th scope="row">
            <user-inline :user="payment.creator_user"></user-inline>
          </th>
          <td align="center">
            <div class="badge badge-info w-32">{{ payment.type }}</div>
          </td>
          <td><money-display>{{ payment.amount }}</money-display></td>
          <td>{{ payment.created_at }}</td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">{{ payment.status }}</div>
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <th>Creator</th>
          <th align="center">Type</th>
          <th>Amount</th>
          <th>Paid on</th>
          <th align="center">Status</th>
        </tr>
      </tfoot>
    </table>
  </div>
  <div v-else class="max-w-lg h-64 bg-gray-100 rounded-xl mx-auto mt-16 flex justify-center flex-col items-center">
    <div class="opacity-40 text-center">
      <icon-user-plus :size="64" class="mx-auto mb-3"></icon-user-plus>
      <div>Payments will appear here. <br> Explore <strong>Featured Creators</strong> to get started.</div>
    </div>
  </div>
</div>
</template>

<script>
export default {
  async asyncData({ $axios }) {
    const payments = await $axios.$get('/api/payments/');
    return { payments };
  },
  head: {
    title: 'Payments'
  }
};
</script>
