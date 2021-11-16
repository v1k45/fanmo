<template>
<div>
  <h1 class="text-2xl font-bold">Subscriptions <span v-if="subscriptions.count">({{ subscriptions.count }})</span></h1>
  <div class="mt-2 font-medium opacity-70">View and manage your subscriptions</div>

  <div class="form-control mt-6">
    <input type="text" placeholder="Search subscriptions" class="input input-bordered">
  </div>
  <div v-if="subscriptions.results.length" class="overflow-x-auto mt-6 border rounded-lg">
    <table class="table table-zebra w-full">
      <thead>
        <tr>
          <th>Creator</th>
          <th align="center">Tier</th>
          <th>Amount</th>
          <th>Last paid on</th>
          <th>Lifetime paid</th>
          <th align="center">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subscription in subscriptions.results" :key="subscription.id">
          <th scope="row">
            <div class="flex items-center space-x-3">
              <div class="avatar">
                <div class="w-12 h-12 mask mask-circle">
                  <img src="http://daisyui.com/tailwind-css-component-profile-2@56w.png" alt="Avatar Tailwind CSS Component">
                </div>
              </div>
              <div class="font-bold">{{ subscription.seller_user.username }}</div>
            </div>
          </th>
          <td align="center">
            <div v-if="subscription.tier" class="badge badge-info w-32">{{ subscription.tier.name }}</div>
            <div v-else class="badge badge-info w-32">No Tier</div>
          </td>
          <td><money-display>{{ subscription.amount }}</money-display></td>
          <td>21st Aug, 2021</td>
          <td><money-display>{{ subscription.amount }}</money-display></td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">{{ subscription.status }}</div>
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <th>Subscriber name</th>
          <th align="center">Tier</th>
          <th>Last paid</th>
          <th>Last paid on</th>
          <th>Lifetime paid</th>
          <th align="center">Status</th>
        </tr>
      </tfoot>
    </table>
  </div>
  <div v-else class="max-w-lg h-64 bg-gray-100 rounded-xl mx-auto mt-16 flex justify-center flex-col items-center">
    <div class="opacity-40 text-center">
      <icon-user-plus :size="64" class="mx-auto mb-3"></icon-user-plus>
      <div>Subscriptions will appear here. <br> Explore <strong>Featured Creators</strong> to get started.</div>
    </div>
  </div>
</div>
</template>

<script>
export default {
  async asyncData({ $axios }) {
    const subscriptions = await $axios.$get('/api/subscriptions/');
    return { subscriptions };
  },
  head: {
    title: 'Subscriptions'
  }
};
</script>
