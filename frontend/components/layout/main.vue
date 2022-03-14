<template>
<div class="flex flex-col min-h-screen">

  <!-- header start -->
  <header class="sticky top-0 z-10 py-2 bg-white shadow-sm">
    <div class="container flex items-center">
      <div v-if="0" class="inline-block text-xl font-bold">
        <div class="sm:hidden">XS</div>
        <div class="hidden sm:inline-block md:hidden">SM</div>
        <div class="hidden md:inline-block lg:hidden">MD</div>
        <div class="hidden lg:inline-block xl:hidden">LG</div>
        <div class="hidden xl:inline-block 2xl:hidden">XL</div>
        <div class="hidden 2xl:inline-block">2XL</div>
      </div>

      <a href="/" class="mr-auto">
        <logo circle class="h-11"></logo>
      </a>

      <nav>
        <button class="p-3 md:hidden text-fm-primary" @click="isNavVisibleMobile = !isNavVisibleMobile;">
          <icon-menu v-if="!isNavVisibleMobile"></icon-menu>
          <icon-x v-else></icon-x>
        </button>
        <ul :class="{
          'text-sm absolute left-0 top-full w-full bg-white space-y-6 p-6': true,
          'md:flex md:items-center md:space-x-12 md:static md:w-auto md:p-0 md:space-y-0': true,
          'hidden': !isNavVisibleMobile,
        }">
          <template v-if="$auth.loggedIn">
            <li class="flex items-center">
              <div class="rounded-full overflow-hidden w-8 h-8">
                <img :src="$auth.user.avatar.small" class="h-full w-full object-cover">
              </div>
              <div class="ml-2">{{ $auth.user.username }}</div>
            </li>
            <li>
              <button class="text-fm-error" title="Log out" @click="$auth.logout('cookie')">
                <IconPower class="inline-block" :stroke-width="3" :size="18"></IconPower>
                <span class="sr-only">Log out</span>
              </button>
            </li>
          </template>
          <template v-else>
            <li><nuxt-link class="unstyled" to="/pricing">Pricing</nuxt-link></li>
            <li><nuxt-link class="unstyled" to="/pricing#comparison">Comparison</nuxt-link></li>
            <li><nuxt-link class="unstyled" to="/login">Login</nuxt-link></li>
            <li>
              <nuxt-link
                to="/register"
                class="unstyled inline-block px-8 py-3 transition-colors rounded-full bg-fm-primary-100 hover:bg-fm-primary-500 hover:text-white">
                Sign up
              </nuxt-link>
            </li>
          </template>
        </ul>
      </nav>
    </div>
  </header>
  <!-- header end -->

  <slot v-if="custom"></slot>
  <template v-else>
    <main v-if="container" class="container py-8 flex-grow">
      <Nuxt></Nuxt>
    </main>
    <Nuxt v-else></Nuxt>
  </template>

  <!-- footer start -->
  <footer class="py-12 mt-auto bg-white border-t">
    <div class="container">
      <div class="flex items-center">
        <div class="mr-auto">
          <logo class="h-7 md:h-9"></logo>
        </div>
        <div class="flex text-black">
          <a href="https://facebook.com/getfanmo" target="_blank" title="Facebook" class="unstyled p-2 rounded-lg hover:bg-blue-500 hover:text-white transition-colors">
            <icon-facebook></icon-facebook>
            <span class="sr-only">Facebook</span>
          </a>
          <a href="https://twitter.com/getfanmo" target="_blank" title="Twitter" class="unstyled p-2 rounded-lg ml-4 hover:bg-sky-500 hover:text-white transition-colors">
            <icon-twitter></icon-twitter>
            <span class="sr-only">Twitter</span>
          </a>
          <a href="https://instagram.com/getfanmo" title="Instagram" class="unstyled p-2 rounded-lg ml-4 hover:bg-violet-500 hover:text-white transition-colors">
            <icon-instagram></icon-instagram>
            <span class="sr-only">Instagram</span>
          </a>
        </div>
      </div>

      <div class="flex flex-wrap items-center mt-2 lg:mt-4">
        <p class="text-xs md:text-sm text-gray-500 mr-auto">Copyright &copy; {{ currentYear }}. All rights reserved.</p>
        <div class="mt-8 lg:mt-0 flex flex-wrap text-black text-sm md:text-base justify-center">
          <nuxt-link class="unstyled py-2 mr-4 hover:text-fm-primary" to="/pricing#faq">FAQ</nuxt-link>
          <a class="unstyled p-2 mr-2 hover:text-fm-primary" href="#">Terms &amp; Conditions</a>
          <a class="unstyled p-2 mr-2 hover:text-fm-primary" href="#">Privacy Policy</a>
          <a class="unstyled p-2 hover:text-fm-primary" href="#">Cancellation policy</a>
        </div>
      </div>
    </div>
  </footer>
  <!-- footer end -->
</div>
</template>

<script>
import {
  Menu as IconMenu, X as IconX, Facebook as IconFacebook,
  Twitter as IconTwitter, Instagram as IconInstagram
} from 'lucide-vue';
export default {
  components: {
    IconMenu,
    IconX,
    IconFacebook,
    IconTwitter,
    IconInstagram
  },
  props: {
    container: { type: Boolean, default: true },
    custom: { type: Boolean, default: false }
  },
  data() {
    return {
      isNavVisibleMobile: false,
      currentYear: new Date().getFullYear()
    };
  }
};
</script>
