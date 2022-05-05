<template>
<!-- sidebar nav items start -->
<ul v-if="type === 'sidebar'">
  <!-- no loggedIn check, consumer should do it -->
  <template v-for="(item, idx) in ($auth.user.is_creator ? nav.creator : nav.supporter)">
    <li
      v-if="!item.url" :key="item.id"
      class="uppercase font-medium text-gray-600 text-sm mb-3"
      :class="{ 'mt-6': idx > 0 }">
      {{ item.label }}
    </li>
    <li v-else :key="item.id" class="mb-1 font-medium">
      <nuxt-link
        :to="item.url" class="unstyled flex items-center py-2 px-4 rounded-xl hover:bg-fm-primary-100"
        exact-active-class="text-white bg-fm-primary pointer-events-none">
        <component :is="item.icon" class="h-6 w-6 mr-3"></component>
        {{ item.label }}
      </nuxt-link>
    </li>
  </template>
</ul>
<!-- sidebar nav items end -->

<!-- bottom pane nav items & hamburger start -->
<div v-else-if="type === 'bottom-pane'" class="h-full">
  <ul class="flex items-center h-full max-w-full sm:max-w-md md:max-w-lg mx-2 sm:mx-auto justify-around">
    <template v-for="(item) in ($auth.user.is_creator ? bottomNav.creator : bottomNav.supporter)">
      <li :key="item.label" class="text-center text-xs sm:text-sm font-medium flex-1 min-w-0">
        <nuxt-link
          :to="item.url" class="unstyled rounded-xl hover:bg-fm-primary-100 focus:bg-fm-primary focus:text-white inline-block px-2 py-2 w-full"
          exact-active-class="text-white bg-fm-primary pointer-events-none">

          <logo
            v-if="item.label === 'Home'" circle uncolored
            class="w-6 h-6 inline -ml-3 transform scale-125 text-inherit">
          </logo>
          <component :is="item.icon" v-else class="h-6 w-6"></component>
          <div class="mt-1 truncate" :title="item.label">{{ item.label }}</div>
        </nuxt-link>
      </li>
    </template>
    <li class="text-center text-sm font-medium flex-1">
      <fm-dropdown placement="top-end">
        <button class="inline-flex items-center p-1 rounded-full border">
          <fm-avatar
            :src="$auth.user.avatar && $auth.user.avatar.small" :name="$auth.user.display_name"
            size="w-9 h-9 mx-auto">
          </fm-avatar>
          <icon-menu class="ml-1 w-4"></icon-menu>
        </button>
        <template #items>
          <template v-for="(item) in ($auth.user.is_creator ? nav.creator : nav.supporter)">
            <fm-dropdown-item
              v-if="!item.url" :key="item.id" static
              class="uppercase font-medium text-gray-600 text-sm min-w-[200px]">
              {{ item.label }}
            </fm-dropdown-item>
            <fm-dropdown-item v-else :key="item.id" class="font-medium !p-0">
              <nuxt-link
                :to="item.url" class="unstyled flex items-center p-3">
                <component :is="item.icon" class="h-6 w-6 mr-3"></component>
                {{ item.label }}
              </nuxt-link>
            </fm-dropdown-item>
          </template>
          <fm-dropdown-divider></fm-dropdown-divider>
          <fm-dropdown-item type="error" class="font-medium flex items-center" @click="$auth.logout('cookie')">
            <icon-power class="h-6 w-6 mr-2 transform scale-75" :stroke-width="3" :size="18"></icon-power>
            Log out
          </fm-dropdown-item>
        </template>
      </fm-dropdown>
    </li>
  </ul>
</div>
<!-- bottom pane nav items & hamburger end -->

<!-- top nav hamburger start -->
<div v-else-if="type === 'hamburger'">
  <fm-dropdown placement="top-end">
    <button class="inline-flex items-center p-1 rounded-full border">
      <fm-avatar
        :src="$auth.user.avatar && $auth.user.avatar.small" :name="$auth.user.display_name"
        size="w-9 h-9 mx-auto">
      </fm-avatar>
      <span class="font-medium ml-2 max-w-[300px] truncate">{{ $auth.user.display_name }}</span>
      <icon-menu class="ml-2 mr-2 w-5"></icon-menu>
    </button>
    <template #items>
      <template v-for="(item) in ($auth.user.is_creator ? nav.creator : nav.supporter)">
        <fm-dropdown-item
          v-if="!item.url" :key="item.id" static
          class="uppercase font-medium text-gray-600 text-sm min-w-[200px]">
          {{ item.label }}
        </fm-dropdown-item>
        <fm-dropdown-item v-else :key="item.id" class="font-medium !p-0">
          <nuxt-link
            :to="item.url" class="unstyled flex items-center p-3">
            <component :is="item.icon" class="h-6 w-6 mr-3"></component>
            {{ item.label }}
          </nuxt-link>
        </fm-dropdown-item>
      </template>
      <fm-dropdown-divider></fm-dropdown-divider>

      <fm-dropdown-item type="error" class="font-medium flex items-center" @click="$auth.logout('cookie')">
        <icon-power class="h-6 w-6 mr-2 transform scale-75" :stroke-width="3" :size="18"></icon-power>
        Log out
      </fm-dropdown-item>
    </template>
  </fm-dropdown>
</div>
<!-- top nav hamburger end -->
</template>

<script>
import { Coins, Home, LayoutList, LayoutTemplate, Sliders, UserCheck, Users, Wallet } from 'lucide-vue';
export default {
  props: {
    type: { type: String, required: true, validator: val => ['sidebar', 'bottom-pane', 'hamburger'].includes(val) }
  },
  data() {
    return {
      nav: {
        creator: [
          { id: 'creator-pages', label: 'Creator pages' },
          { id: 'dashboard', label: 'Dashboard', icon: Home, url: '/' },
          { id: 'members', label: 'Members', icon: Users, url: '/members/' },
          { id: 'creator-donations', label: 'Donations', icon: Coins, url: '/received-donations/' },
          { id: 'earnings', label: 'Earnings', icon: Wallet, url: '/earnings/' },
          { id: 'profile', label: 'Profile', icon: LayoutTemplate, url: { name: 'profile' } },
          { id: 'settings', label: 'Settings', icon: Sliders, url: '/404/' },

          { id: 'supporter-pages', label: 'Supporter pages' },
          { id: 'feed', label: 'Feed', icon: LayoutList, url: '/feed/' },
          { id: 'memberships', label: 'Memberships', icon: UserCheck, url: '/memberships/' },
          { id: 'supporter-donations', label: 'Donations', icon: Coins, url: '/sent-donations/' }
        ],
        supporter: [
          { id: 'dashboard', label: 'Dashboard', icon: Home, url: '/' },
          { id: 'memberships', label: 'Memberships', icon: UserCheck, url: '/memberships/' },
          { id: 'donations', label: 'Donations', icon: Coins, url: '/sent-donations/' }
        ]
      },
      bottomNav: {
        creator: [
          { id: 'members', label: 'Members', icon: Users, url: '/members/' },
          { id: 'donations', label: 'Donations', icon: Coins, url: '/received-donations/' },
          { id: 'home', label: 'Home', url: '/' }, // has special behavior based on the label
          { id: 'earnings', label: 'Earnings', icon: Wallet, url: '/earnings/' }
        ],
        supporter: [
          { id: 'memberships', label: 'Memberships', icon: UserCheck, url: '/memberships/' },
          { id: 'donations', label: 'Donations', icon: Coins, url: '/sent-donations/' },
          { id: 'home', label: 'Home', url: '/' }, // has special behavior based on the label
          { id: 'settings', label: 'Settings', icon: Sliders, url: '/404/' }
        ]
      }
    };
  }
};
</script>
