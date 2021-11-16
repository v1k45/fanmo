<template>
<div>
  <h1 class="text-2xl font-bold">Payouts <span v-if="payouts.count">({{ payouts.count }})</span></h1>
  <div class="mt-2 font-medium opacity-70">View your payouts</div>

  <div class="form-control mt-6">
    <input type="text" placeholder="Search payouts" class="input input-bordered">
  </div>
  <div v-if="payouts.results.length" class="overflow-x-auto mt-6 border rounded-lg">
    <table class="table table-zebra w-full">
      <thead>
        <tr>
          <th>Supporter</th>
          <th align="center">Type</th>
          <th>Amount</th>
          <th>Original Amount</th>
          <th>Paid on</th>
          <th align="center">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="payout in payouts.results" :key="payout.id">
          <th scope="row">
            <div class="flex items-center space-x-3">
              <div class="avatar">
                <div class="w-12 h-12 mask mask-circle">
                  <img src="http://daisyui.com/tailwind-css-component-profile-2@56w.png" alt="Avatar Tailwind CSS Component">
                </div>
              </div>
              <div v-if="payout.payment.buyer_user" class="font-bold">{{ payout.payment.buyer_user.username }}</div>
            </div>
          </th>
          <td align="center">
            <div class="badge badge-info w-32">{{ payout.payment.type }}</div>
          </td>
          <td><money-display>{{ payout.amount }}</money-display></td>
          <td><money-display>{{ payout.payment.amount }}</money-display></td>
          <td>{{ payout.created_at }}</td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">{{ payout.status }}</div>
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <th>Supporter</th>
          <th align="center">Type</th>
          <th>Amount</th>
          <th>Original Amount</th>
          <th>Paid on</th>
          <th align="center">Status</th>
        </tr>
      </tfoot>
    </table>
  </div>
  <div v-else class="max-w-lg h-64 bg-gray-100 rounded-xl mx-auto mt-16 flex justify-center flex-col items-center">
    <div class="opacity-40 text-center">
      <icon-user-plus :size="64" class="mx-auto mb-3"></icon-user-plus>
      <div>Payouts will appear here. <br> Explore <strong>Featured Creators</strong> to get started.</div>
    </div>
  </div>
</div>
</template>

<script>
export default {
  async asyncData({ $axios }) {
    const payouts = await $axios.$get('/api/payouts/');
    return { payouts };
  },
  head: {
    title: 'Payouts'
  }
};
</script>
