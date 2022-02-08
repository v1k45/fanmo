<template>
<div>

  <!-- header start -->
  <header class="sticky top-0 z-10 py-2 bg-white shadow-sm">
    <div class="container flex items-center">
      <div v-if="false" class="inline-block text-xl font-bold">
        <div class="sm:hidden">XS</div>
        <div class="hidden sm:inline-block md:hidden">SM</div>
        <div class="hidden md:inline-block lg:hidden">MD</div>
        <div class="hidden lg:inline-block xl:hidden">LG</div>
        <div class="hidden xl:inline-block 2xl:hidden">XL</div>
        <div class="hidden 2xl:inline-block">2XL</div>
      </div>

      <a href="/" class="mr-auto">
        <img src="~/assets/marketing/fanmo.svg" class="h-7" alt="Fanmo logo">
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
          <li><nuxt-link to="/pricing">Pricing</nuxt-link></li>
          <li><nuxt-link to="/pricing#comparison">Comparison</nuxt-link></li>
          <li><nuxt-link to="/login">Login</nuxt-link></li>
          <li>
            <nuxt-link
              to="/signup"
              class="inline-block px-8 py-3 transition-colors rounded-full bg-fm-primary-100 hover:bg-fm-primary-500 hover:text-white">
              Sign up
            </nuxt-link>
          </li>
        </ul>
      </nav>
    </div>
  </header>
  <!-- header end -->

  <Nuxt></Nuxt>

  <!-- footer start -->
  <footer class="py-6 bg-fm-primary-100">
    <div class="container flex flex-wrap justify-center font-semibold items-center space-x-8 text-fm-primary-900">
      <nuxt-link class="py-2" to="/pricing#faq">FAQ</nuxt-link>
      <a class="py-2" href="#">Privacy Policy</a>
      <a class="py-2" href="#">Terms &amp; Conditions</a>
      <a class="py-2" href="#">Cancellation policy</a>
    </div>
  </footer>
  <!-- footer end -->
</div>
</template>

<script>
import { Menu as IconMenu, X as IconX } from 'lucide-vue';
export default {
  components: {
    IconMenu,
    IconX
  },
  layout: 'empty',
  auth: false,
  data() {
    return {
      isNavVisibleMobile: false
    };
  }
};
</script>
