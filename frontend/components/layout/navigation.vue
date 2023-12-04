<template>
<!-- sidebar nav items start -->
<ul v-if="type === 'sidebar'">
  <!-- no loggedIn check, consumer should do it -->
  <li>
    <fm-avatar :src="$auth.user.avatar && $auth.user.avatar.small" :name="$auth.user.display_name" size="h-24 w-24" class="mx-auto"></fm-avatar>
  </li>
  <li class="text-center mt-2">
    <nuxt-link v-if="$auth.user.is_creator" :to="`/${$auth.user.username}`">
      <fm-button>
        <icon-layout-template class="h-4 w-4 -mt-0.5"></icon-layout-template> View page
      </fm-button>
    </nuxt-link>
    <div v-else class="text-black font-medium truncate">{{ $auth.user.display_name }}</div>
  </li>
  <li class="my-3">
    <hr>
  </li>
  <template v-for="(item, idx) in ($auth.user.is_creator ? nav.creator : nav.supporter)">
    <template v-if="item.id === 'profile'"></template>  <!-- don't render profile in sidebar -->
    <li
      v-else-if="!item.url" :key="item.id"
      class="uppercase font-medium text-gray-600 text-sm mb-3"
      :class="{ 'mt-6': idx > 0 }">
      {{ item.label }}
    </li>
    <li v-else :key="item.id" class="mb-1 font-medium">
      <nuxt-link
        :to="item.url" class="unstyled flex items-center py-2 px-4 rounded-xl hover:bg-fm-primary-100"
        active-class="text-white bg-fm-primary pointer-events-none">
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
            v-if="item.id === 'home'" circle uncolored
            class="w-6 h-6 inline -ml-3 transform scale-125 text-inherit">
          </logo>
          <component :is="item.icon" v-else class="h-6 w-6"></component>
          <div class="mt-1 truncate" :title="item.label">{{ item.label }}</div>
        </nuxt-link>
      </li>
    </template>
    <li class="text-center text-sm font-medium flex-1">
      <button class="inline-flex items-center p-1 rounded-full border" @click="isBottomPaneDrawerVisible = true;">
        <fm-avatar
          :src="$auth.user.avatar && $auth.user.avatar.small" :name="$auth.user.display_name"
          size="w-9 h-9 mx-auto">
        </fm-avatar>
        <icon-menu class="ml-1 w-4"></icon-menu>
      </button>
    </li>
  </ul>

  <fm-dialog v-model="isBottomPaneDrawerVisible" dialog-class="!max-w-xs" drawer no-padding>
    <div class="!border-t-0 mt-6">
      <div>
        <!-- v-if is a workaround to get this to re-render so the font-size is recalculated when the dialog is shown -->
        <fm-avatar v-if="isBottomPaneDrawerVisible" :src="$auth.user.avatar && $auth.user.avatar.small" :name="$auth.user.display_name" size="h-24 w-24" class="mx-auto"></fm-avatar>
        <div class="mx-4 mt-2 text-xl font-semibold text-center">{{ $auth.user.display_name }}</div>
      </div>
      <div class="text-center mt-2">
        <nuxt-link v-if="$auth.user.is_creator" :to="`/${$auth.user.username}`">
          <fm-button>
            <icon-layout-template class="h-4 w-4 -mt-0.5"></icon-layout-template> View page
          </fm-button>
        </nuxt-link>
        <div v-else>
          <div class="text-black font-medium px-4">{{ $auth.user.display_name }}</div>
          <hr class="mt-6">
        </div>
      </div>
      <template v-for="(item) in ($auth.user.is_creator ? nav.creator : nav.supporter)">
        <template v-if="item.id === 'profile'"></template>  <!-- don't render profile in sidebar -->
        <div
          v-else-if="!item.url" :key="item.id"
          class="uppercase font-medium text-gray-600 text-sm mt-2 px-4 py-3 border-b">
          {{ item.label }}
        </div>
        <nuxt-link
          v-else :key="item.id" :to="item.url"
          class="unstyled flex items-center border-l border-b border-r bg-white px-4 py-3 hover:bg-gray-200 font-medium" actionable
          @click.native="isBottomPaneDrawerVisible = false;">
          <component :is="item.icon" class="h-6 w-6 mr-3"></component>
          {{ item.label }}
        </nuxt-link>
      </template>
      <div class="font-medium flex items-center px-4 py-3 border-b text-fm-error hover:bg-fm-error hover:text-white" actionable @click="logout">
        <icon-power class="h-6 w-6 mr-2 transform scale-75" :stroke-width="3" :size="18"></icon-power>
        Log out
      </div>
    </div>
    <layout-footer class="py-6 border-t-0"></layout-footer>
  </fm-dialog>
</div>
<!-- bottom pane nav items & hamburger end -->

<!-- top nav hamburger start -->
<div v-else-if="['hamburger', 'hamburger-minimal'].includes(type)">
  <fm-dropdown placement="bottom-end">
    <button class="inline-flex items-center p-1 rounded-full border bg-white">
      <fm-avatar
        :src="$auth.user.avatar && $auth.user.avatar.small" :name="$auth.user.display_name"
        size="mx-auto" :class="{ 'w-9 h-9': type === 'hamburger', 'w-8 h-8': type === 'hamburger-minimal' }">
      </fm-avatar>
      <span v-if="type === 'hamburger'" class="font-medium ml-2 max-w-[300px] truncate">{{ $auth.user.display_name }}</span>
      <icon-menu class="ml-2 mr-2 w-5"></icon-menu>
    </button>
    <template #items>
      <template v-for="(item) in ($auth.user.is_creator ? nav.creator : nav.supporter)">
        <fm-dropdown-item
          v-if="!item.url" :key="item.id" static
          class="uppercase font-medium text-gray-600 text-sm">
          {{ item.label }}
        </fm-dropdown-item>
        <fm-dropdown-item v-else :key="item.id" class="font-medium min-w-[200px] !p-0">
          <nuxt-link
            :to="item.url" class="unstyled flex items-center p-3">
            <component :is="item.icon" class="h-6 w-6 mr-3"></component>
            {{ item.label }}
          </nuxt-link>
        </fm-dropdown-item>
      </template>
      <fm-dropdown-divider></fm-dropdown-divider>

      <fm-dropdown-item type="error" class="font-medium flex items-center" @click="logout">
        <icon-power class="h-6 w-6 mr-2 transform scale-75" :stroke-width="3" :size="18"></icon-power>
        Log out
      </fm-dropdown-item>
    </template>
  </fm-dropdown>
</div>
<!-- top nav hamburger end -->

<!-- anonymous hamburger start -->
<div v-else-if="type === 'anonymous-hamburger'">
  <fm-dropdown placement="top-end">
    <button class="inline-flex items-center p-1 rounded-full border bg-white">
      <fm-avatar size="mx-auto w-8 h-8"></fm-avatar>
      <icon-menu class="ml-2 mr-2 w-5"></icon-menu>
    </button>
    <template #items>
      <template v-for="(item) in nav.anonymous">
        <fm-dropdown-item
          v-if="!item.url" :key="item.id" static
          class="uppercase font-medium text-gray-600 text-sm">
          {{ item.label }}
        </fm-dropdown-item>
        <fm-dropdown-item v-else :key="item.id" class="font-medium min-w-[200px] !p-0">
          <nuxt-link
            :to="item.url" class="unstyled flex items-center p-3">
            <component :is="item.icon" class="h-6 w-6 mr-3"></component>
            {{ item.label }}
          </nuxt-link>
        </fm-dropdown-item>
      </template>
      <fm-dropdown-divider></fm-dropdown-divider>

      <fm-dropdown-item static class="font-medium flex items-center !pt-0">
        <span class="text-sm">Powered by</span> <logo class="inline-block h-em"></logo>
      </fm-dropdown-item>
    </template>
  </fm-dropdown>
</div>
<!-- anonymous hamburger end -->
</template>

<script>
import { Coins, Home, LayoutList, LayoutTemplate, Sliders, UserCheck, Users, Wallet, LogIn, UserPlus } from 'lucide-vue';
import { delay } from '~/utils';
export default {
  props: {
    type: {
      type: String,
      required: true,
      validator: val => ['sidebar', 'bottom-pane', 'hamburger', 'hamburger-minimal', 'anonymous-hamburger'].includes(val)
    }
  },
  data() {
    return {
      isBottomPaneDrawerVisible: false
    };
  },
  computed: {
    nav() {
      const { user, loggedIn } = this.$auth;
      if (!loggedIn) return {
        anonymous: [
          { id: 'login', label: 'Login', icon: LogIn, url: '/login/' },
          { id: 'register', label: 'Sign up', icon: UserPlus, url: '/register/' },
          { id: 'landing', label: 'Fanmo home', icon: Home, url: '/' }
        ],
        creator: [],
        supporter: []
      };
      return {
        creator: [
          { id: 'creator-pages', label: 'Creator pages' },
          { id: 'dashboard', label: 'Dashboard', icon: Home, url: '/dashboard/' },
          { id: 'posts', label: 'Posts', icon: LayoutList, url: '/posts/' },
          { id: 'members', label: 'Members', icon: Users, url: '/members/' },
          { id: 'creator-donations', label: 'Tips', icon: Coins, url: '/received-tips/' },
          { id: 'earnings', label: 'Earnings', icon: Wallet, url: '/earnings/' },
          { id: 'profile', label: 'View page', icon: LayoutTemplate, url: `/${user.username}` },
          { id: 'settings', label: 'Settings', icon: Sliders, url: '/settings/' },

          { id: 'supporter-pages', label: 'Supporter pages' },
          { id: 'feed', label: 'Feed', icon: LayoutList, url: '/feed/' },
          { id: 'memberships', label: 'Memberships', icon: UserCheck, url: '/memberships/' },
          { id: 'supporter-donations', label: 'Tips', icon: Coins, url: '/sent-tips/' }
        ],
        supporter: [
          { id: 'feed', label: 'Feed', icon: LayoutList, url: '/feed/' },
          { id: 'memberships', label: 'Memberships', icon: UserCheck, url: '/memberships/' },
          { id: 'donations', label: 'Tips', icon: Coins, url: '/sent-tips/' },
          { id: 'settings', label: 'Settings', icon: Sliders, url: '/settings/' }
        ]
      };
    },
    bottomNav() {
      return {
        creator: [
          { id: 'members', label: 'Members', icon: Users, url: '/members/' },
          { id: 'donations', label: 'Tips', icon: Coins, url: '/received-tips/' },
          { id: 'home', label: 'Home', url: '/dashboard/' }, // has special behavior based on the id
          { id: 'earnings', label: 'Earnings', icon: Wallet, url: '/earnings/' }
        ],
        supporter: [
          { id: 'memberships', label: 'Memberships', icon: UserCheck, url: '/memberships/' },
          { id: 'donations', label: 'Tips', icon: Coins, url: '/sent-tips/' },
          { id: 'home', label: 'Feed', url: '/feed/' }, // has special behavior based on the id
          { id: 'settings', label: 'Settings', icon: Sliders, url: '/settings/' }
        ]
      };
    }
  },
  methods: {
    async logout() {
      await this.$axios.$post('/api/auth/logout/');
      await this.$auth.logout();
      await delay();
      location.reload();
    }
  }
};
</script>
