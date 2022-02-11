<template>
<main>

  <!-- hero start -->
  <section class="relative flex flex-wrap py-8 lg:py-24 xl:py-36 items-center min-h-[550px] 2xl:max-w-7xl mx-auto">
    <img src="~/assets/marketing/bg.png" :class="{
      'w-auto mx-auto max-h-72': true,
      'md:max-h-80': true,
      'lg:absolute lg:top-1/2 lg:transform lg:-translate-y-1/2 lg:right-0 lg:max-w-[50%] lg:max-h-full -z-10': true
    }" alt="Cheerful animated character representing a creator sitting in front of the computer">
    <div class="container">
      <div class="text-center lg:max-w-lg lg:text-left">
        <h1 class="mb-6 text-4xl font-semibold leading-tight font-title sm:text-5xl lg:text-6xl">Home for your most passionate fans</h1>

        <p class="mb-8 leading-relaxed sm:text-lg">Simplest way to offer memberships, accept donations and post member-exclusive content.</p>

        <a href="#" class="inline-flex items-center px-10 py-4 mx-auto text-lg text-white transition-colors rounded-full lg:mx-0 bg-fm-primary hover:bg-fm-primary-600">
          Register Now <icon-arrow-right class="inline-block ml-3"></icon-arrow-right>
        </a>
      </div>
      <div class="flex flex-col items-center justify-center mt-12 mb-12 space-y-3 lg:justify-start sm:flex-row sm:space-y-0 sm:space-x-6 lg:mb-0">
        <div class="flex items-center w-48 sm:w-auto">
          <icon-verified :size="28" class="inline-block mr-1 fill-current text-fm-success-600 stroke-white"></icon-verified>
          <div><span class="text-fm-success-600">4.9%</span> platform fee</div>
        </div>
        <div class="flex items-center w-48 sm:w-auto">
          <icon-verified :size="28" class="inline-block mr-1 fill-current text-fm-success-600 stroke-white"></icon-verified>
          <div>No extra costs</div>
        </div>
        <div class="flex items-center w-48 sm:w-auto">
          <icon-verified :size="28" class="inline-block mr-1 fill-current text-fm-success-600 stroke-white"></icon-verified>
          <div>No processing fee</div>
        </div>
      </div>
    </div>
  </section>
  <!-- hero end -->


  <!-- boasting start -->
  <section class="py-24" style="background: linear-gradient(180deg, #F2F2FF 0%, rgba(241, 248, 255, 0) 79.31%);">
    <div class="container text-center">
      <h2 class="text-3xl leading-snug sm:text-4xl lg:text-5xl font-title">Managing fans has never been <br> this easy</h2>
      <img src="~/assets/marketing/dashboard-illustration.png" alt="Illustrative layout of the platform" class="mx-auto">
      <p class="mt-12 sm:text-xl lg:text-2xl leading-relaxed">Fanmo is refreshing and easy to use, yet <br> powerful enough for all your needs.</p>
    </div>
  </section>
  <!-- boasting end -->

  <!-- feature: memberships start -->
  <section class="pb-24">
    <div class="container">
      <div class="row items-center justify-center">
        <div class="col-12 md:col-8 xl:col-7 order-2 md:order-1 text-center md:text-left">
          <header>
            <h2 class="inline-block md:block font-title text-gray-500 text-2xl lg:text-3xl">Memberships <div aria-hidden="true" class="w-8 border-b-2 md:border-b-4 -mt-1 border-fm-primary"></div></h2>
            <h3 class="font-bold mt-8 text-2xl sm:text-3xl lg:text-4xl">Make your fans feel special 🌟</h3>
          </header>
          <p class="text-base lg:text-xl mt-8">
            Offer monthly memberships for different pricing tiers. Make a steady monthly income while offering exclusive content and experience based on
            membership tiers.
          </p>
        </div>
        <div class="col-8 sm:col-6 md:col-4 xl:offset-1 order-1 md:order-2" aria-hidden="true">
          <img src="~/assets/marketing/memberships.png" class="mx-auto">
        </div>
      </div>
    </div>
  </section>
  <!-- feature: memberships end -->

  <!-- feature: donations start -->
  <section class="pb-24">
    <div class="container">
      <div class="row items-center justify-center">
        <div class="col-8 sm:col-6 md:col-4" aria-hidden="true">
          <img src="~/assets/marketing/money.png" alt="" class="mx-auto">
        </div>
        <div class="col-12 md:col-8 xl:col-7 xl:offset-1 text-center md:text-left">
          <header>
            <h2 class="inline-block md:block font-title text-gray-500 text-2xl lg:text-3xl">Donations <div aria-hidden="true" class="w-8 border-b-2 md:border-b-4 -mt-1 border-fm-primary"></div></h2>
            <h3 class="font-bold mt-8 text-2xl sm:text-3xl lg:text-4xl">Accept Donations 💸</h3>
          </header>
          <p class="text-base lg:text-xl mt-8">
            Let your fans show you some love by donating whatever amount they like. Showcase your fan donations and messages.
          </p>
        </div>
      </div>
    </div>
  </section>
  <!-- feature: donations end -->

  <!-- feature: posts & comments start -->
  <section class="pb-24">
    <div class="container">
      <div class="row items-center justify-center">
        <div class="col-12 md:col-8 xl:col-6 order-2 md:order-1 text-center md:text-left">
          <header>
            <h2 class="inline-block md:block font-title text-gray-500 text-2xl lg:text-3xl">Publish exclusive content <div aria-hidden="true" class="w-8 border-b-2 md:border-b-4 -mt-1 border-fm-primary"></div></h2>
            <h3 class="font-bold mt-8 text-2xl sm:text-3xl lg:text-4xl">Engage with fans 🎙️</h3>
          </header>
          <p class="text-base lg:text-xl mt-8">
            Post exclusive and private content for your fans and keep in touch by interacting with them using comments.
          </p>
        </div>
        <div class="mb-8 md:mb-0 col-6 md:col-4 xl:offset-1 order-1 md:order-2" aria-hidden="true">
          <img src="~/assets/marketing/posts.png" class="mx-auto">
        </div>
      </div>
    </div>
  </section>
  <!-- feature: posts & comments end -->

  <!-- fee comparison start -->
  <!-- TODO: finish -->
  <section v-if="false" class="py-24">
    <div class="container flex space-x-12">
      <div>
        <div class="flex justify-center flex-grow space-x-4 basis-0">
          <div class="flex flex-col justify-between py-8 space-y-8 font-semibold">
            <div class="flex items-center flex-grow">Fanmo</div>
            <div class="flex items-center flex-grow">Patreon</div>
            <div class="flex items-center flex-grow">YouTube</div>
          </div>

          <div class="flex flex-col justify-around py-8 space-y-8 h-80 w-96 bg-fm-primary-50 rounded-xl">
            <div style="background: linear-gradient(90deg, #3DF19B -42.97%, #3DA5F1 134.38%);" class="flex items-center justify-end flex-grow w-2/6 px-3 text-white rounded-r-md">Rs. 23,000</div>
            <div style="background: linear-gradient(89.52deg, #F9C88E 1.16%, #FF4A31 101.75%);" class="flex items-center justify-end flex-grow w-4/6 px-3 text-white rounded-r-md">Rs. 230,000</div>
            <div style="background: linear-gradient(89.52deg, #F9C88E 1.16%, #FF4A31 101.75%);" class="flex items-center justify-end flex-grow w-5/6 px-3 text-white rounded-r-md">Rs. 23,00,00</div>
          </div>
        </div>

      </div>

      <div class="flex-grow basis-0">
        <h1 class="text-6xl font-semibold font-title">Stop losing money</h1>
        <div class="mt-8 text-xl">Check how much money you are losing on other platforms</div>

        <div class="mt-12">
          <label for="subscribers-slider" class="block mb-4 text-xl font-bold">Subscribers</label>
          <div class="relative h-6 bg-gray-200 rounded-xl">
            <div class="absolute w-6 h-10 cursor-grab rounded-xl -top-2 bg-fm-info left-1/3"></div>
          </div>
        </div>

        <div class="mt-16">
          <label for="price-slider" class="block mb-4 text-xl font-bold">Subscription price</label>
          <div class="relative h-6 bg-gray-200 rounded-xl">
            <div class="absolute w-6 h-10 cursor-grab rounded-xl -top-2 bg-fm-info"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
  <!-- fee comparison end -->

  <!-- why fanmo start -->
  <section class="py-24 bg-fm-primary-50">
    <div class="container">
      <h2 class="mb-6 text-4xl leading-tight font-title text-center lg:text-left sm:text-5xl lg:text-7xl">Why Fanmo?</h2>

      <ul class="text-base lg:text-2xl py-4 lg:py-8 space-y-4 lg:space-y-8">
        <li class="flex items-center">
          <icon-verified class="w-8 h-8 lg:w-12 lg:h-12 flex-shrink-0 inline-block mr-4 fill-current text-fm-success-600 stroke-white"></icon-verified>
          <span>
            <span class="font-bold text-title">Lowest platform fee.</span>
            Without losing any features.
          </span>
        </li>
        <li class="flex items-center">
          <icon-verified class="w-8 h-8 lg:w-12 lg:h-12 flex-shrink-0 inline-block mr-4 fill-current text-fm-success-600 stroke-white"></icon-verified>
          <span>
            <span class="font-bold text-title">Fastest payouts.</span>
            Get money in your bank account within 2 days of payment.
          </span>
        </li>
        <li class="flex items-center">
          <icon-verified class="w-8 h-8 lg:w-12 lg:h-12 flex-shrink-0 inline-block mr-4 fill-current text-fm-success-600 stroke-white"></icon-verified>
          <span>
            <span class="font-bold text-title">100% yours.</span>
            Export all your data, any time you like.
          </span>
        </li>
        <li class="flex items-center">
          <icon-verified class="w-8 h-8 lg:w-12 lg:h-12 flex-shrink-0 inline-block mr-4 fill-current text-fm-success-600 stroke-white"></icon-verified>
          <span>
            <span class="font-bold text-title">Responsive support</span>
            Get all the help and support you need, in any mode you prefer.
          </span>
        </li>
      </ul>

      <div class="text-center lg:text-left">
        <a class="inline-flex items-center mt-8 px-10 py-4 mx-auto lg:text-lg text-white transition-colors rounded-full lg:mx-0 bg-fm-primary hover:bg-fm-primary-600">
          Register Now <icon-arrow-right class="inline-block ml-3"></icon-arrow-right>
        </a>
      </div>
    </div>
  </section>
  <!-- why fanmo end -->
</main>
</template>

<script>
import { ArrowRight as IconArrowRight, Verified as IconVerified } from 'lucide-vue';
export default {
  components: {
    IconArrowRight,
    IconVerified
  },
  layout: 'marketing',
  auth: false
};
</script>
