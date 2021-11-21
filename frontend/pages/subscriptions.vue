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
          <th>Cycle End</th>
          <th align="center">Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subscription in subscriptions.results" :key="subscription.id">
          <th scope="row">
            <div class="flex items-center space-x-3">
              <div class="avatar">
                <div class="w-12 h-12 mask mask-circle">
                  <img :src="subscription.seller_user.avatar.small" alt="Avatar Tailwind CSS Component">
                </div>
              </div>
              <div class="font-bold">{{ subscription.seller_user.username }}</div>
            </div>
          </th>
          <td align="center">
            <div v-if="subscription.tier" class="badge badge-info badge-lg w-32">{{ subscription.tier.name }}</div>
            <div v-else class="badge badge-ghost w-32">No Tier</div>
          </td>
          <td><money-display>{{ subscription.amount }}</money-display></td>
          <td>{{ subscription.cycle_end_at }}</td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">{{ subscription.status }}</div>
          </td>
          <td>
            <div class="dropdown dropdown-end ml-auto">
              <button class="m-1 btn btn-sm btn-ghost">
                <icon-more-horizontal></icon-more-horizontal>
              </button>
              <ul tabindex="0" class="p-2 shadow menu dropdown-content bg-base-100 rounded-box w-52">
                <li class="text-error"><a @click="cancel(subscription.id)">Cancel</a></li>
              </ul>
            </div>
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <th>Creator</th>
          <th align="center">Tier</th>
          <th>Amount</th>
          <th>Cycle End</th>
          <th align="center">Status</th>
          <th></th>
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
import faker from 'faker';

const USE_FAKE = false;

export default {
  async asyncData({ $axios }) {
    const subscriptions = await $axios.$get('/api/subscriptions/');
    if (USE_FAKE) {
      subscriptions.results = Array(50).fill(1).map(() => ({
        seller_user: { username: faker.internet.userName() },
        tier: faker.random.arrayElement([
          { name: faker.random.arrayElement(['', 'Gold', 'Silver', 'Bronze', 'Premium', 'Diamond']) },
          null
        ]),
        amount: faker.random.number([5, 20000]),
        status: faker.random.arrayElement(['scheduled', 'paid', 'accepted', 'active', 'inactive'])
      }));
      subscriptions.count = subscriptions.results.length;
    }

    return { subscriptions };
  },
  head: {
    title: 'Subscriptions'
  },
  methods: {
    async cancel(subscriptionId) {
      try {
        await this.$axios.$post(`/api/subscriptions/${subscriptionId}/cancel/`);
        alert('Cancelled');
      } catch (error) {
        alert('Error');
      }
    }
  }
};
</script>
