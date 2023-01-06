<template>
<main>

  <!-- hero start -->
  <section class="relative flex flex-wrap py-8 lg:py-24 xl:py-36 items-center min-h-[550px] 2xl:max-w-7xl mx-auto z-0">
    <img src="~/assets/marketing/hero.optimized.svg" :class="{
      'w-auto mx-auto max-h-72 px-4': true,
      'md:max-h-80': true,
      'lg:absolute lg:top-1/2 lg:transform lg:-translate-y-1/2 lg:right-0 lg:max-w-[50%] lg:max-h-full -z-10': true
    }" alt="Cheerful animated character representing a creator sitting in front of the computer">
    <div class="container">
      <div class="text-center lg:max-w-lg lg:text-left">
        <h1 class="mb-6 text-4xl font-semibold leading-tight font-title sm:text-5xl lg:text-6xl">Home for your most passionate fans</h1>

        <p class="mb-8 leading-relaxed sm:text-lg">Simplest way to offer memberships, accept tips and post member-exclusive content.</p>

        <nuxt-link
          :to="$auth.loggedIn ? '/dashboard' : '/register'"
          class="unstyled inline-flex items-center px-10 py-4 mx-auto text-lg text-white rounded-full lg:mx-0 bg-fm-primary transform transition-transform hover:scale-105">
          {{ $auth.loggedIn ? 'Go to Dashboard' : 'Register Now' }}
        </nuxt-link>
      </div>
      <div class="flex flex-col items-center justify-center mt-12 mb-12 space-y-3 lg:justify-start sm:flex-row sm:space-y-0 sm:space-x-6 lg:mb-0">
        <div class="flex items-center w-48 sm:w-auto">
          <icon-verified :size="28" class="inline-block mr-1 fill-current text-fm-success-600 stroke-white"></icon-verified>
          <div><span class="text-fm-success-700">4.9%</span> platform fee</div>
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

  <!-- feature: featured creators -->
  <section class="py-24" style="background: linear-gradient(180deg, #F2F2FF 0%, rgba(241, 248, 255, 0) 79.31%);">
    <div class="container">
      <div class="row items-center justify-center">
        <h2 class="mb-10 text-4xl leading-tight font-title text-center sm:text-4xl md:text-5xl lg:text-6xl">What is Fanmo?</h2>
        <div class="max-w-2xl mx-auto mb-8 sm:text-lg text-center">
          <p>
            Fanmo is a platform for creators who want to earn a steady income by offering monthly memberships to their dedicated fans.
            With Fanmo, you can follow your passion and build a sustainable income stream without the constraints of social media algorithms.
          </p>
          <p class="mt-6">
            Fanmo makes it easy and fun to share exclusive content and grow your audience.
            Try Fanmo now and start your journey towards the financial freedom you deserve.
          </p>
        </div>
        <template v-if="creators.length">
          <h2 class="mb-10 text-2xl leading-tight font-title text-center sm:text-2xl md:text-3xl lg:text-4xl">Featured Creators</h2>
          <div class="flex justify-center justify-evenly space-y-8 md:space-y-0 md:flex-row flex-col">
            <nuxt-link v-for="creator in creators" :key="creator.username" :to="`/${creator.username}`" class="unstyled transform transition-transform hover:scale-105">
              <div class="flex items-center flex-col">
                <fm-avatar :src="creator.avatar && creator.avatar.medium" :name="creator.display_name" size="w-24 h-24 lg:w-32 lg:h-32"></fm-avatar>
                <div class="text-2xl text-black font-bold mt-2">{{ creator.display_name }}</div>
                <div v-if="creator.one_liner" class="text-gray-500">{{ creator.one_liner }}</div>
              </div>
            </nuxt-link>
          </div>
        </template>
      </div>
    </div>
  </section>
  <!-- feature: featured creators end -->

  <!-- fee comparison start -->
  <section class="py-14" style="background: linear-gradient(180deg, #F2F2FF 0%, rgba(241, 248, 255, 0) 79.31%);">
    <div class="container">
      <div class="lg:hidden text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-semibold font-title">Stop losing money</h1>
        <div class="mt-4">Use the sliders to see how well Fanmo compares to other platforms in terms of platform fee.</div>
      </div>

      <marketing-fee-revenue-viz>
        <template #above-controls>
          <div class="hidden lg:block">
            <h1 class="text-3xl md:text-4xl lg:text-5xl font-semibold font-title">Stop losing money</h1>
            <div class="mt-4 text-lg">Use the sliders to see how Fanmo compares to other platforms in terms of platform fee.</div>
          </div>
        </template>
      </marketing-fee-revenue-viz>
    </div>
  </section>
  <!-- fee comparison end -->

  <!-- boasting start -->
  <!-- <section v-if="false" class="py-24" style="background: linear-gradient(180deg, #F2F2FF 0%, rgba(241, 248, 255, 0) 79.31%);">
    <div class="container text-center">
      <h2 class="text-3xl leading-snug sm:text-4xl lg:text-5xl font-title">Managing fans has never been <br> this easy</h2>
      <img src="~/assets/marketing/dashboard-illustration.png" alt="Illustrative layout of the platform" class="mx-auto">
      <p class="mt-12 sm:text-xl lg:text-2xl leading-relaxed">Fanmo is refreshing and easy to use, yet <br> powerful enough for all your needs.</p>
    </div>
  </section> -->
  <!-- boasting end -->

  <!-- feature: memberships start -->
  <section class="py-14">
    <div class="container">
      <div class="row items-center justify-center">
        <div class="col-12 md:col-8 xl:col-6 order-2 md:order-1 text-center md:text-left">
          <header>
            <h2 class="font-bold mt-6 text-2xl leading-snug sm:text-3xl sm:leading-snug lg:leading-relaxed">
              Make your fans feel special with
              <span class="inline-block text-white px-3 rounded bg-fm-primary leading-snug">tiered memberships</span>
              🌟
            </h2>
          </header>
          <p class="text-base lg:text-xl mt-6">
            Offer monthly memberships for different pricing tiers. Make a steady monthly income while offering exclusive content and experience based on
            membership tiers.
          </p>
        </div>
        <div class="col-10 sm:col-6 md:col-4 xl:col-5 xl:offset-1 order-1 md:order-2" aria-hidden="true">
          <img src="~/assets/marketing/memberships.optimized.svg" class="mx-auto">
        </div>
      </div>
    </div>
  </section>
  <!-- feature: memberships end -->

  <!-- feature: donations start -->
  <section class="py-14">
    <div class="container">
      <div class="row items-center justify-center">
        <div class="col-10 sm:col-6 md:col-4 xl:col-5" aria-hidden="true">
          <img src="~/assets/marketing/donations.optimized.svg" alt="" class="mx-auto">
        </div>
        <div class="col-12 md:col-8 xl:col-6 xl:offset-1 text-center md:text-left">
          <header>
            <h2 class="font-bold mt-6 text-2xl leading-snug sm:text-3xl sm:leading-snug lg:leading-relaxed">
              Let your fans support you in more ways with
              <span class="inline-block text-white px-4 leading-snug rounded bg-fm-success-700">tips</span>
              💸
            </h2>
          </header>
          <p class="text-base lg:text-xl mt-6">
            Let your fans show you some love by tipping whatever amount they like. Showcase your fan tips and messages.
          </p>
        </div>
      </div>
    </div>
  </section>
  <!-- feature: donations end -->

  <!-- feature: posts & comments start -->
  <section class="py-14">
    <div class="container">
      <div class="row items-center justify-center">
        <div class="col-12 md:col-8 xl:col-6 order-2 md:order-1 text-center md:text-left">
          <header>

            <h2 class="font-bold mt-6 text-2xl leading-snug sm:text-3xl sm:leading-snug lg:leading-relaxed">
              Engage with your fans through
              <span class="inline-block text-white px-4 leading-snug rounded bg-fm-error">
                exclusive content
              </span>
              🎙️
            </h2>
          </header>
          <p class="text-base lg:text-xl mt-6">
            Post exclusive and private content of any type for your fans and keep in touch by interacting with them using comments.
          </p>
        </div>
        <div class="mb-8 md:mb-0 col-10 md:col-4 xl:col-5 xl:offset-1 order-1 md:order-2" aria-hidden="true">
          <img src="~/assets/marketing/posts.optimized.svg" class="mx-auto max-h-48 lg:max-h-full">
        </div>
      </div>
    </div>
  </section>
  <!-- feature: posts & comments end -->

  <!-- why fanmo start -->
  <section class="py-24 bg-fm-primary-50">
    <div class="container">
      <h2 class="mb-6 text-3xl leading-tight font-title text-center sm:text-4xl md:text-5xl lg:text-6xl">Why choose Fanmo?</h2>

      <div class="flex flex-wrap text-center text-base md:text-lg lg:text-xl py-4 lg:py-8">
        <div class="flex flex-col items-center w-full md:w-1/3 my-8 space-y-2">
          <icon-indian-rupee class="w-8 h-8 lg:w-12 lg:h-12 text-fm-primary"></icon-indian-rupee>
          <div class="font-bold text-title">Lowest platform fee</div>
          <div class="mt-2 text-gray-500">Earn more without losing any features. Straight forward pricing without any hidden transaction processing fees.</div>
        </div>
        <div class="flex flex-col items-center w-full md:w-1/3 my-8 space-y-2">
          <icon-line-chart class="w-8 h-8 lg:w-12 lg:h-12 text-fm-primary"></icon-line-chart>
          <div class="font-bold text-title">Insightful Dashboard</div>
          <div class="mt-2 text-gray-500">Real-time graphs, stats and activities of your memberships and payment trends. All in one place.</div>
        </div>
        <div class="flex flex-col items-center w-full md:w-1/3 my-8 space-y-2">
          <icon-inbox class="w-8 h-8 lg:w-12 lg:h-12 text-fm-primary"></icon-inbox>
          <div class="font-bold text-title">Email notifications</div>
          <div class="mt-2 text-gray-500">Deliver your posts instantly to your members as newsletters. Get notified whenever someone supports you.</div>
        </div>
        <div class="flex flex-col items-center w-full md:w-1/3 my-8 space-y-2">
          <icon-download class="w-8 h-8 lg:w-12 lg:h-12 text-fm-primary"></icon-download>
          <div class="font-bold text-title">100% yours</div>
          <div class="mt-2 text-gray-500">Take back control of your transactional and membership data. Export all your data as CSV, any time you like.</div>
        </div>
        <div class="flex flex-col items-center w-full md:w-1/3 my-8 space-y-2">
          <icon-zap class="w-8 h-8 lg:w-12 lg:h-12 text-fm-primary"></icon-zap>
          <div class="font-bold text-title">Fastest payouts</div>
          <div class="mt-2 text-gray-500">Get money in you bank account within two working days of any membership or tip payment.</div>
        </div>
        <div class="flex flex-col items-center w-full md:w-1/3 my-8 space-y-2">
          <icon-life-buoy class="w-8 h-8 lg:w-12 lg:h-12 text-fm-primary"></icon-life-buoy>
          <div class="font-bold text-title">Responsive support</div>
          <div class="mt-2 text-gray-500">Need help with something? Questions? Have feature suggestions? We are just an e-mail away.</div>
        </div>
      </div>

      <div class="text-center">
        <nuxt-link
          :to="$auth.loggedIn ? '/dashboard' : '/register'"
          class="unstyled inline-flex items-center mt-8 px-10 py-4 mx-auto lg:text-lg text-white rounded-full lg:mx-0 bg-fm-primary transform transition-transform hover:scale-105">
          {{ $auth.loggedIn ? 'Go to Dashboard' : 'Register Now' }}
        </nuxt-link>
      </div>
    </div>
  </section>
  <!-- why fanmo end -->
</main>
</template>

<script>
import { Verified as IconVerified } from 'lucide-vue';
export default {
  components: {
    IconVerified
  },
  layout: 'marketing',
  auth: false,
  data() {
    return {
      creators: []
    };
  },
  async mounted() {
    try {
      this.creators = (await this.$axios.$get('/api/users/?is_creator=true&is_featured=true')).results;
    } catch (e) {
      this.creators = [];
    }
  }
};
</script>
