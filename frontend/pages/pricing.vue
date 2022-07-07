<template>
<main>

  <!-- hero start -->
  <section class="py-16 lg:py-24 min-h-[550px] bg-fm-primary-50">
    <div class="container flex flex-wrap">
      <div>
        <div class="lg:max-w-lg">
          <h1 class="inline-block md:block font-title text-gray-500 text-2xl lg:text-3xl mb-6 lg:mb-12">Pricing</h1>
          <h1 class="mb-6 lg:mb-12 text-4xl font-semibold leading-tight font-title sm:text-5xl lg:text-6xl">Simple and most affordable</h1>

          <p class="mb-8 leading-relaxed sm:text-lg">
            Fanmo takes a small platform fee from your earnings. <br><br>
            Unlike other platforms, with Fanmo you don't have to guess the money you'll get in your bank account.
          </p>
        </div>
        <div class="flex flex-col mt-6 lg:mt-12 mb-6 space-y-3 sm:flex-row sm:space-y-0 sm:space-x-6 lg:mb-0">
          <div class="flex items-center">
            <icon-verified :size="28" class="flex-shrink-0 inline-block mr-2 sm:mr-1 fill-current text-fm-success-600 stroke-white"></icon-verified>
            <div>No payment processing fee</div>
          </div>
          <div class="flex items-center">
            <icon-verified :size="28" class="flex-shrink-0 inline-block mr-2 sm:mr-1 fill-current text-fm-success-600 stroke-white"></icon-verified>
            <div>No setup fee</div>
          </div>
          <div class="flex items-center">
            <icon-verified :size="28" class="flex-shrink-0 inline-block mr-2 sm:mr-1 fill-current text-fm-success-600 stroke-white"></icon-verified>
            <div>No limits</div>
          </div>
        </div>
      </div>
      <div class="flex justify-center lg:justify-end flex-grow mt-8 lg:mt-0">
        <div class="max-w-sm w-full rounded-[3rem] px-8 py-12 text-white" style="background: linear-gradient(167.27deg, #7E7BF7 -11.87%, #4A47DD 119.25%);">
          <div class="text-center text-2xl flex items-center justify-center">
            <strong class="text-5xl mr-2">4.9%</strong> platform fee
          </div>
          <div class="inline-block text-sm mt-8">Included Features <div aria-hidden="true" class="w-6 border-b-2 border-white"></div></div>

          <ul class="space-y-4 mt-6 font-bold">
            <li
              v-for="feature in ['Membership tiers', 'Donations', 'Posts', 'Fast payouts', 'Various payment methods', 'Responsive support']" :key="feature"
              class="flex items-center">
              <icon-check class="mr-3"></icon-check> {{ feature }}
            </li>
          </ul>

          <nuxt-link
            :to="$auth.loggedIn ? '/dashboard' : '/register'"
            class="unstyled flex justify-center items-center mt-8 px-10 py-4 mx-auto lg:text-lg text-fm-primary rounded-full lg:mx-0 bg-white transform transition-transform hover:scale-105">
            {{ $auth.loggedIn ? 'Go to Dashboard' : 'Register Now' }}
            <icon-arrow-right class="inline-block ml-3"></icon-arrow-right>
          </nuxt-link>
        </div>
      </div>
    </div>
  </section>
  <!-- hero end -->

  <!-- comparison start -->
  <section id="comparison" class="py-24">
    <div class="container">
      <h2 class="text-center mb-8 md:mb-16 text-3xl leading-snug sm:text-4xl lg:text-5xl font-title">Earn more without compromising on features</h2>

      <div class="comparison">
        <table>
          <thead>
            <tr>
              <th></th>
              <th>
                <logo class="h-em mx-auto"></logo>
              </th>
              <th>Patreon</th>
              <th>YouTube</th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <th>Memberships</th>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
            </tr>
            <tr>
              <th>Donations</th>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
              <td><icon-x-circle class="icon-x"></icon-x-circle></td>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
            </tr>
            <tr>
              <th>Exclusive posts</th>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
            </tr>
            <tr>
              <th>Fee</th>
              <td class="font-bold text-fm-success-600"><span class="text-xl md:text-3xl">4.9%</span></td>
              <td>
                10.9% (+ $0.30 per payment)
                <span class="cursor-pointer" title="8% (platform fee) + 2.9% (payment fee) + $0.30 (per payment)">
                  <icon-info class="h-4 w-4 text-fm-info fill-current stroke-white"></icon-info>
                </span>
              </td>
              <td>30%</td>
            </tr>
            <tr>
              <th>Payouts</th>
              <td>Within 2 days</td>
              <td>Upto 30 days</td>
              <td>Upto 30 days</td>
            </tr>
            <tr>
              <th>Payment methods</th>
              <td>Credit Card, Debit Card, <br> Net banking, UPI</td>
              <td>Credit Card, PayPal</td>
              <td>Credit Card, Debit Card, <br> Net banking, UPI</td>
            </tr>
            <tr>
              <th>Currency</th>
              <td>INR</td>
              <td>USD</td>
              <td>INR</td>
            </tr>
            <tr>
              <th>International payments</th>
              <td>Coming soon</td>
              <td>Yes</td>
              <td>Yes</td>
            </tr>
            <tr>
              <th>Discord integration</th>
              <td>Coming soon</td>
              <td>Yes</td>
              <td><icon-x-circle class="icon-x"></icon-x-circle></td>
            </tr>
            <tr>
              <th>Signup required</th>
              <td>No (Automatic signup)</td>
              <td>Yes</td>
              <td>Yes</td>
            </tr>
            <tr>
              <th>Live support</th>
              <td><icon-check-circle-2 class="icon-check"></icon-check-circle-2></td>
              <td><icon-x-circle class="icon-x"></icon-x-circle></td>
              <td><icon-x-circle class="icon-x"></icon-x-circle></td>
            </tr>
            <tr class="hidden lg:table-row">
              <th></th>
              <td>
                <nuxt-link
                  :to="$auth.loggedIn ? '/dashboard' : '/register'"
                  class="unstyled inline-flex items-center px-10 py-4 my-6 text-lg mx-auto text-white transition-colors rounded-full bg-fm-primary hover:bg-fm-primary-600">
                  {{ $auth.loggedIn ? 'Go to Dashboard' : 'Register Now' }}
                  <icon-arrow-right class="inline-block ml-3"></icon-arrow-right>
                </nuxt-link>
              </td>
              <td></td>
              <td></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="text-center lg:hidden">
        <nuxt-link
          :to="$auth.loggedIn ? '/dashboard' : '/register'"
          class="unstyled inline-flex items-center px-10 py-3 my-6 text-sm text-white transition-colors rounded-full lg:mx-0 bg-fm-primary hover:bg-fm-primary-600">
          {{ $auth.loggedIn ? 'Go to Dashboard' : 'Register Now' }}
        </nuxt-link>
      </div>

    </div>
  </section>
  <!-- comparison end -->

  <!-- faq start -->
  <div id="faq" class="py-24 bg-fm-primary-50">
    <div class="container">
      <h2 class="text-center mb-8 md:mb-16 text-2xl leading-snug sm:text-3xl lg:text-4xl font-bold">
        Frequently asked questions
        <div aria-hidden="true" class="mx-auto w-16 mt-2 border-b-2 md:border-b-4 border-fm-primary"></div>
      </h2>

      <!-- questions start -->
      <article v-for="(faq, idx) in faqs" :key="faq.question" class="bg-white rounded-lg mb-4 max-w-3xl mx-auto">
        <button
          class="p-5 pb-4 flex text-left w-full items-center"
          :title="idx === faqExpandedIdx ? 'Collapse this FAQ' : 'Expand this FAQ'"
          @click="faqExpandedIdx = idx === faqExpandedIdx ? -1 : idx;">
          <h2 class="md:text-lg font-bold flex-grow">{{ faq.question }}</h2>
          <div class="flex-shrink-0 text-fm-primary">
            <icon-chevron-down class="transform transition-transform" :class="{ 'rotate-180': idx === faqExpandedIdx }"></icon-chevron-down>
          </div>
        </button>
        <div
          class="transition-[max-height] duration-300 overflow-hidden"
          :class="faqExpandedIdx === idx ? 'max-h-52' : 'max-h-0'">
          <p class="text-sm md:text-base px-5 pb-5" v-html="faq.answer"></p>
        </div>
      </article>
      <!-- questions end -->

    </div>
  </div>
  <!-- faq end -->

  <!-- final CTA start -->
  <div class="py-20" style="background: linear-gradient(205.42deg, #8D8BFF -23.63%, #4845DE 162.06%);">
    <div class="container text-center text-white">
      <h2 class="text-center mb-8 text-3xl leading-snug sm:text-4xl lg:text-6xl font-title text-white">
        Start saving money!
      </h2>
      <p class="mb-12 text-lg">It's free to sign up and takes less than 5 minutes to get started.</p>

      <nuxt-link
        :to="$auth.loggedIn ? '/dashboard' : '/register'"
        class="unstyled inline-flex justify-center items-center px-10 py-4 mx-auto lg:text-lg text-fm-primary rounded-full lg:mx-0 bg-white transform transition-transform hover:scale-105">
        {{ $auth.loggedIn ? 'Go to dashboard' : 'Register for free' }}
        <icon-arrow-right class="inline-block ml-3"></icon-arrow-right>
      </nuxt-link>
    </div>
  </div>
  <!-- final CTA end -->
</main>
</template>

<script>
import {
  ArrowRight as IconArrowRight, Verified as IconVerified, Check as IconCheck,
  CheckCircle2 as IconCheckCircle2, XCircle as IconXCircle, Info as IconInfo,
  ChevronDown as IconChevronDown
} from 'lucide-vue';
export default {
  components: {
    IconArrowRight,
    IconVerified,
    IconCheck,
    IconCheckCircle2,
    IconXCircle,
    IconInfo,
    IconChevronDown
  },
  layout: 'marketing',
  auth: false,
  data() {
    return {
      faqExpandedIdx: 0,
      faqs: [
        {
          question: 'How do I get paid?',
          answer: 'All payments are instantly transferred to your bank account. It could take up to 2 business days for the payouts to reach your account.'
        },
        {
          question: 'How much does Fanmo cost?',
          answer: 'We take a 4.9% processing fee from the payments. If a fan pays Rs. 1000 to you, you\'ll receive Rs. 951 in your account. There is no additional cost to use the platform.'
        },
        {
          question: 'Do you support UPI?',
          answer: `
            Yes! We love UPI. Your fans can use any UPI app for paying for donations. <br><br>
            For memberships, currently only PhonePe, Amazon Pay, Paytm and BHIM UPI are supported. This list will expand as soon as other UPI apps start supporting UPI AutoPay.
          `
        },
        {
          question: 'Is there a minimum or maximum limit of fans I can have?',
          answer: 'No! You can start small with a few fans or go wild with thousands of them. Pricing and support experience will remain top-notch, irrespective of your size.'
        },
        {
          question: 'Why is it so cheap? What\'s the catch?',
          answer: `
            Our pricing is driven by our optimized technology. We charge enough to keep the lights on and deliver features that add value.
            We don't believe in gouging creators to line our pockets.
            <br><br>
            So rest assured, there's no catch! We believe creators should not lose a large chunk of their hard earned money just to communicate with their fans.
          `
        },

        {
          question: 'Will you increase your platform fee in the future?',
          answer: `
            No. We don't foresee the need to increase our fee in the near future.
            We will continue to evaluate our offering and make sure we offer the best value to creators.
            <br><br>
            Rest assured, if we do end up increasing it, our existing creators will continue with the old fee forever without losing any features.
          `
        },
        {
          question: 'Will you help my fans with their questions and issues?',
          answer: 'Of course! Your fans can contact us through email and other means, we usually respond within 2 hours. We also have a Help Site where we have detailed articles.'
        },
        {
          question: 'Is Fanmo right for me? Why should I use it instead of Patreon?',
          answer: `
            Fanmo is a cheaper and easier alternative to Patreon, specifically for Indian users. We support practically all Indian payment methods, thus making it easier for your fans to support you.
            <br><br>
            Unlike Patreon, with Fanmo you can also accept donations from your fans.
          `
        }
      ]
    };
  }
};
</script>
<style scoped lang="scss">
.comparison {
  @apply max-w-full overflow-auto relative;

  table {
    @apply mx-auto;
  }
  // all cells
  th, td {
    @apply align-middle;
  }
  // column headers
  thead th {
    @apply text-center font-normal py-6 text-title;
    @apply lg:text-2xl;

    &:first-child {
      @apply sticky left-0 bg-white;
    }
  }

  tbody {
    // all body cells
    th, td {
      height: 4rem;
      @apply px-6 border-b;
    }
    // row headers
    th {
      @apply text-sm text-left font-normal sticky left-0 bg-white px-2;
      @apply sm:text-base md:px-6;
    }
    // body cells
    td {
      @apply text-center text-xs sm:text-sm;
    }

    // no border on cells of last row
    tr:last-child {
      th, td {
        @apply border-b-0;
      }
    }

    // to make the icons respect cell alignment
    svg {
      @apply inline-block;
    }
  }

  // common icon styles
  .icon-check {
    @apply text-gray-400 fill-current stroke-white h-7 w-7;
  }
  .icon-x {
    @apply text-fm-error fill-current stroke-white h-7 w-7;
  }

  // fanmo column specific styles from here on out

  th:nth-child(2), td:nth-child(2) {
    @apply border-b-0 bg-gray-100;
    .icon-check { // special icon color for check marks for emphasis
      @apply text-fm-success-600;
    }
  }

  // rounded top and bottom corners
  thead th:nth-child(2) {
    @apply rounded-t-3xl;
  }
  tbody tr:last-child td:nth-child(2) {
    @apply rounded-b-3xl;
  }
}
</style>
