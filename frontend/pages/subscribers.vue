<template>
<div>
  <h1 class="text-2xl font-bold">Subscribers <span v-if="subscribers.count">({{ subscribers.count }})</span></h1>
  <div class="mt-2 font-medium opacity-70">View and manage your subscribers</div>

  <div class="form-control mt-6">
    <input type="text" placeholder="Search subscribers" class="input input-bordered">
  </div>
  <div v-if="subscribers.results.length" class="overflow-x-auto mt-6 border rounded-lg">
    <table class="table table-zebra w-full">
      <thead>
        <tr>
          <th>Subscriber</th>
          <th align="center">Tier</th>
          <th>Amount</th>
          <th>Last paid on</th>
          <th>Lifetime paid</th>
          <th align="center">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subscriber in subscribers.results" :key="subscriber.id">
          <th scope="row">
            <div class="flex items-center space-x-3">
              <div class="avatar">
                <div class="w-12 h-12 mask mask-circle">
                  <img src="http://daisyui.com/tailwind-css-component-profile-2@56w.png" alt="Avatar Tailwind CSS Component">
                </div>
              </div>
              <div class="font-bold">{{ subscriber.buyer_user.username }}</div>
            </div>
          </th>
          <td align="center">
            <div v-if="subscriber.tier" class="badge badge-info w-32">{{ subscriber.tier.name }}</div>
            <div v-else class="badge badge-info w-32">No Tier</div>
          </td>
          <td><money-display>{{ subscriber.amount }}</money-display></td>
          <td>21st Aug, 2021</td>
          <td><money-display>{{ subscriber.amount }}</money-display></td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">{{ subscriber.status }}</div>
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <th>Subscriber</th>
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
      <div>Subscribers will appear here. <br> Explore <strong>Featured Creators</strong> to get started.</div>
    </div>
  </div>
</div>
</template>

<script>
export default {
  async asyncData({ $axios }) {
    const subscribers = await $axios.$get('/api/subscribers/');
    return { subscribers };
  },
  head: {
    title: 'Subscribers'
  }
};
</script>
