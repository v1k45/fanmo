<template>
<div>
  <div v-if="false" class="row row-cols-5 g-4">
    <div>
      <nuxt-link to="/" class="flex flex-col border items-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <IconHome :size="36"></IconHome>
        <div class="mt-2">Home</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/profile" class="flex flex-col border items-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-layout :size="36"></icon-layout>
        <div class="mt-2">Profile</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/subscriptions" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-user-plus :size="36"></icon-user-plus>
        <div class="mt-2">Subscriptions</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/subscribers" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-users :size="36"></icon-users>
        <div class="mt-2">Subscribers</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/payments" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-wallet :size="36"></icon-wallet>
        <div class="mt-2">Payments</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/payouts" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-indian-rupee :size="36"></icon-indian-rupee>
        <div class="mt-2">Payouts</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/tiers" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <IconListMinus :size="36"></IconListMinus>
        <div class="mt-2">Manage tiers</div>
      </nuxt-link>
    </div>
    <div>
      <nuxt-link to="/settings" class="flex flex-col border items-center text-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <icon-settings :size="36"></icon-settings>
        <div class="mt-2">Settings</div>
      </nuxt-link>
    </div>
  </div>

  <div v-if="false" class="text-center pt-16">
    <div class="mb-6">
      Sign up by clicking on the button below to get started!
    </div>
    <nuxt-link to="/register" class="btn px-10 animate-bounce">Sign up</nuxt-link>
  </div>

  <h1 class="text-2xl font-bold my-4">Featured Creators</h1>
  <div class="row row-cols-5 g-4">
    <div v-for="user in creators.results" :key="user.id">
      <nuxt-link :to="`/${user.username}`" class="flex flex-col border items-center shadow-md bg-white rounded-lg p-8 hover:scale-105 transition-transform transform">
        <div class="avatar">
          <div class="w-24 h-24 border rounded-full">
            <img :src="user.avatar.medium">
          </div>
        </div>
        <div class="mt-2">{{ user.username }}</div>
      </nuxt-link>
    </div>
  </div>

  <h1 class="text-2xl font-bold my-8">Posts</h1>
  <div v-if="posts.count" class="mt-8 max-w-lg">
    <post v-for="post in posts.results" :key="post.id" :post="post" class="mb-6"></post>
  </div>
</div>
</template>

<script>
export default {
  auth: false,
  async asyncData({ $axios }) {
    const creators = await $axios.$get('/api/users/?creator=true');
    const posts = await $axios.$get('/api/posts/');
    return { creators, posts };
  },
  head: {
    title: 'Home'
  }
};
</script>
