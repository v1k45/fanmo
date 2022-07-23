<template>
<footer class="py-12 bg-white border-t">
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
        <a href="https://twitter.com/getfanmo" target="_blank" title="Twitter" class="unstyled p-2 rounded-lg ml-1 md:ml-4 hover:bg-sky-500 hover:text-white transition-colors">
          <icon-twitter></icon-twitter>
          <span class="sr-only">Twitter</span>
        </a>
        <a href="https://instagram.com/getfanmo" title="Instagram" class="unstyled p-2 rounded-lg ml-1 md:ml-4 hover:bg-violet-500 hover:text-white transition-colors">
          <icon-instagram></icon-instagram>
          <span class="sr-only">Instagram</span>
        </a>
      </div>
    </div>

    <div class="flex flex-wrap items-center mt-2 lg:mt-4">
      <p class="text-xs md:text-sm text-gray-500 mr-auto">Copyright &copy; {{ currentYear }}. All rights reserved.</p>
      <div class="mt-8 lg:mt-0 flex flex-wrap text-black text-sm md:text-base justify-center">
        <nuxt-link class="unstyled py-2 mr-4 hover:text-fm-primary" to="/pricing#faq">FAQ</nuxt-link>
        <nuxt-link class="unstyled p-2 mr-2 hover:text-fm-primary" to="/terms">Terms &amp; Conditions</nuxt-link>
        <nuxt-link class="unstyled p-2 mr-2 hover:text-fm-primary" to="/privacy">Privacy Policy</nuxt-link>
        <nuxt-link class="unstyled p-2 hover:text-fm-primary" to="/refunds">Cancellation policy</nuxt-link>
      </div>
    </div>
  </div>
</footer>
</template>

<script>
export default {
  data() {
    return {
      currentYear: new Date().getFullYear()
    };
  }
};
</script>
