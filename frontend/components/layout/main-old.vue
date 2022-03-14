<template>
<div class="bg-neutral min-h-screen flex flex-col">

  <div class="navbar text-neutral-content">
    <div class="flex-1 px-2 mx-2">
      <nuxt-link to="/" class="text-2xl md:text-3xl font-extrabold">fanmo</nuxt-link>
    </div>
    <div class="flex-none hidden px-2 mx-2 lg:flex">
      <div v-if="$auth.loggedIn" class="flex items-stretch norm">
        <div class="flex items-center">
          <div class="avatar">
            <div class="rounded-full w-8 h-8">
              <img :src="$auth.user.avatar.small">
            </div>
          </div>
          <div class="text-sm font-semibold ml-2 max-w-xs truncate">{{ $auth.user.username }}</div>
        </div>
        <div class="tooltip tooltip-left tooltip-primary ml-4" data-tip="Sign out">
          <button class="btn btn-square btn-sm rounded-btn normal-case text-error bg-neutral-focus" @click="$auth.logout('cookie')">
            <IconPower :stroke-width="3" :size="18"></IconPower>
          </button>
        </div>
      </div>
      <div v-else class="flex items-stretch norm">
        <nuxt-link to="/login" class="btn btn-ghost btn-sm rounded-btn normal-case mr-3">Sign in</nuxt-link>
        <nuxt-link to="/register" class="btn btn-info btn-sm rounded-btn normal-case">Create an Account</nuxt-link>
      </div>
    </div>
    <div class="flex-none">
      <label for="main-drawer" class="btn btn-square btn-ghost drawer-button lg:hidden">
        <icon-menu class="inline-block w-6 h-6 stroke-current"></icon-menu>
      </label>
    </div>
  </div>

  <main class="flex-grow h-0">
    <div class="drawer drawer-mobile h-full">
      <input id="main-drawer" type="checkbox" class="drawer-toggle">

      <aside v-if="$auth.loggedIn" class="drawer-side scrollbar">
        <label for="main-drawer" class="drawer-overlay z-10 lg:z-auto"></label>
        <ul class="w-24 bg-neutral text-neutral-content z-10 lg:z-auto">
          <li class="m-1 px-1 py-2 rounded hover:bg-neutral-focus">
            <div>
              <nuxt-link to="/" class="flex flex-col items-center">
                <IconHome :size="22"></IconHome>
                <div class="text-2xs">Home</div>
              </nuxt-link>
            </div>
          </li>
          <li class="m-1 px-1 py-2 rounded hover:bg-neutral-focus">
            <div>
              <nuxt-link :to="`/${$auth.user.username}`" class="flex flex-col items-center">
                <icon-layout :size="22"></icon-layout>
                <div class="text-2xs">Profile</div>
              </nuxt-link>
            </div>
          </li>
          <li class="m-1 px-1 py-2 rounded hover:bg-neutral-focus">
            <div>
              <nuxt-link to="/subscriptions" class="flex flex-col items-center text-center">
                <icon-user-plus :size="22"></icon-user-plus>
                <div class="text-2xs leading-normal">Subscriptions</div>
              </nuxt-link>
            </div>
          </li>
          <li class="m-1 px-1 py-2 rounded hover:bg-neutral-focus">
            <div>
              <nuxt-link to="/subscribers" class="flex flex-col items-center text-center">
                <icon-users :size="22"></icon-users>
                <div class="text-2xs leading-normal">Subscribers</div>
              </nuxt-link>
            </div>
          </li>
          <li class="m-1 px-1 py-2 rounded hover:bg-neutral-focus">
            <div>
              <nuxt-link to="/payments" class="flex flex-col items-center text-center">
                <icon-wallet :size="22"></icon-wallet>
                <div class="text-2xs leading-normal">Payments</div>
              </nuxt-link>
            </div>
          </li>
          <li class="m-1 px-1 py-2 rounded hover:bg-neutral-focus">
            <div>
              <nuxt-link to="/payouts" class="flex flex-col items-center text-center">
                <icon-indian-rupee :size="22"></icon-indian-rupee>
                <div class="text-2xs leading-normal">Payouts</div>
              </nuxt-link>
            </div>
          </li>
          <li class="m-1 px-1 py-2 rounded hover:bg-neutral-focus">
            <div>
              <nuxt-link to="/tiers" class="flex flex-col items-center text-center">
                <IconListMinus :size="22"></IconListMinus>
                <div class="text-2xs leading-normal">Manage tiers</div>
              </nuxt-link>
            </div>
          </li>
          <li class="m-1 px-1 py-2 rounded hover:bg-neutral-focus">
            <div>
              <nuxt-link to="/settings" class="flex flex-col items-center text-center">
                <icon-settings :size="22"></icon-settings>
                <div class="text-2xs leading-normal">Settings</div>
              </nuxt-link>
            </div>
          </li>
        </ul>
      </aside>

      <div v-if="noContainer" class="drawer-content bg-gray-50 rounded-tl-3xl scrollbar">
        <Nuxt></Nuxt>
      </div>
      <div v-else class="drawer-content py-8 px-4 md:px-6 bg-gray-50 rounded-tl-3xl scrollbar">
        <div class="container">
          <Nuxt></Nuxt>
        </div>
      </div>
    </div>
  </main>

</div>
</template>

<script>
export default {
  props: {
    noContainer: { type: Boolean, default: false }
  }
};
</script>
