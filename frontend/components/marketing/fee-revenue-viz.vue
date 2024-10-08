<template>
<div>
  <div class="relative flex flex-wrap lg:flex-nowrap space-y-2 lg:space-y-0 lg:space-x-12 items-center">

    <div class="w-full lg:w-7/12 xl:w-7/12 pb-8">

      <div class="flex justify-center flex-grow space-x-2 md:space-x-6 basis-0">

        <div class="flex flex-col justify-between py-4 space-y-4 md:py-8 md:space-y-8">
          <div v-for="platform in data" :key="platform.id" class="flex items-center justify-end flex-grow text-xs md:text-base">
            <span :class="{ 'font-bold text-xs md:text-xl': platform.id === 'fanmo' }">
              {{ platform.name }}
            </span>
          </div>
        </div>

        <div class="flex-grow relative">
          <div class="flex flex-col justify-around py-4 space-y-4 md:py-8 md:space-y-8 h-56 md:h-80 bg-fm-primary-50 rounded-xl">
            <div
              v-for="platform in barData" :key="platform.id"
              :style="{ background: platform.barBackground, width: `${platform.width}%` }"
              class="flex items-center justify-end flex-grow px-3 text-white rounded-r-md relative transition-[width] duration-1000 text-xs md:text-base">
              <template v-if="platform.width < 20 || platform.id === 'fanmo'">
                <span>&nbsp;</span> <!-- to maintain equal height -->
                <div
                  class="absolute left-full ml-4 whitespace-nowrap"
                  :class="{
                    'text-fm-success-600 font-bold md:text-lg': platform.id === 'fanmo',
                    'text-black': platform.id !== 'fanmo'
                  }">
                  {{ inrFormat.format(platform.fee) }}
                </div>
              </template>
              <template v-else>{{ inrFormat.format(platform.fee) }}</template>
            </div>
          </div>
          <div class="absolute w-full text-center text-xs md:text-sm top-full mt-2">Platform fee</div>
        </div>

        <div class="relative">
          <div class="flex flex-col justify-between py-4 space-y-4 md:py-8 md:space-y-8 font-semibold w-20 md:w-32 text-xs md:text-lg relative h-full">
            <div v-for="platform in barData" :key="platform.id" class="flex items-center flex-grow">
              <span v-if="platform.id === 'fanmo'" class="text-black">{{ inrFormat.format(platform.earned) }}</span>
              <span v-else class="text-gray-400">{{ inrFormat.format(platform.earned) }}</span>
            </div>
          </div>
          <div class="absolute w-full text-left text-xs md:text-sm top-full mt-2">Your earnings</div>
        </div>

      </div>

    </div>

    <div class="w-full lg:w-5/12 xl:w-5/12 pb-6">

      <slot name="above-controls"></slot>

      <div class="mt-12">
        <div class="flex items-end mb-4 md:mb-6 md:text-lg xl:text-xl font-bold">
          <label for="subscribers-slider" class="block mr-auto">Total subscribers</label>
          <label for="subscribers-input" class="sr-only">Total subscribers</label>
          <input
            id="subscribers-input" v-model.number="subscriberCount" type="number"
            class="w-28 h-10 border-gray-200 border-2 rounded-lg text-xl font-bold text-fm-info"
            min="1" max="1000" @focus="$event.target.select();">
        </div>
        <input
          id="subscribers-slider" v-model.number="subscriberCount"
          type="range" name="subscribers-slider" class="slider"
          min="1" max="1000">
      </div>

      <div class="mt-12">
        <div class="flex items-end mb-4 md:mb-6 md:text-lg xl:text-xl font-bold">
          <label for="price-slider" class="block mr-auto">Monthly subscription price</label>
          <label for="price-input" class="sr-only">Monthly subscription price</label>
          <div class="flex items-center text-fm-success-600">
            <icon-indian-rupee class="h-full mr-1"></icon-indian-rupee>
            <input
              id="price-input" v-model.number="subscriptionPrice" type="number"
              class="w-28 h-10 border-gray-200 border-2 rounded-lg font-bold text-xl text-fm-success-600"
              min="10" max="1000" @focus="$event.target.select();">
          </div>
        </div>
        <input
          id="price-slider" v-model.number="subscriptionPrice"
          type="range" name="price-slider" class="slider"
          min="10" max="1000">
      </div>
    </div>
  </div>
  <div class="text-xs text-gray-400">* USD based flat fee calculation for Patreon assumes 1 USD ≈ 80 INR conversion rate.</div>
</div>
</template>

<script>
import { IndianRupee as IconIndianRupee } from 'lucide-vue';

const getValueByPercent = (total, percent) => percent * (total / 100);
const round = num => Number(num.toFixed(2));
const USD_TO_INR_PRICE = 80;
const inrFormat = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default {
  components: {
    IconIndianRupee
  },
  data() {
    const subscriberCount = 500;
    const subscriptionPrice = 150;
    return {
      data: [
        {
          id: 'fanmo',
          name: 'Fanmo',
          barBackground: 'linear-gradient(90deg, #3DF19B -42.97%, #3DA5F1 134.38%)',
          getFee: (subscribers, price) => getValueByPercent(subscribers * price, 4.9)
        },
        {
          id: 'patreon',
          name: 'Patreon',
          barBackground: 'linear-gradient(89.52deg, #F9C88E 1.16%, #FF4A31 101.75%)',
          getFee: (subscribers, price) => {
            const baseFee = getValueByPercent(subscribers * price, 8); // base fee of 8% on the total

            const priceInUSD = price / USD_TO_INR_PRICE;
            // for transactions over $3, the % fee is 2.9% and 5% otherwise
            const txnFeePercent = priceInUSD > 3 ? 2.9 : 5;
            // for transactions over $3, the flat fee is $0.30 and $0.10 otherwise
            const txnFeeStatic = (priceInUSD > 3 ? 0.30 : 0.10) * USD_TO_INR_PRICE;

            const paymentProcessingFee = (getValueByPercent(price, txnFeePercent) * subscribers) + (txnFeeStatic * subscribers);

            return baseFee + paymentProcessingFee;
          }
        },
        {
          id: 'youtube',
          name: 'YouTube',
          barBackground: 'linear-gradient(89.52deg, #F9C88E 1.16%, #FF4A31 101.75%)',
          getFee: (subscribers, price) => getValueByPercent(subscribers * price, 30)
        }
      ],
      subscriberCount,
      subscriptionPrice,

      internalSubscriberCount: subscriberCount,
      internalSubscriptionPrice: subscriptionPrice,

      inrFormat,
      rerender: 0
    };
  },
  computed: {
    barData() {
      let { internalSubscriberCount, internalSubscriptionPrice } = this;
      if (!internalSubscriberCount) internalSubscriberCount = 0;
      if (!internalSubscriptionPrice) internalSubscriptionPrice = 0;
      const total = round(internalSubscriberCount * internalSubscriptionPrice);
      let maxFee = Number.NEGATIVE_INFINITY;
      const computed = this.data.map(platform => {
        const fee = round(platform.getFee(internalSubscriberCount, internalSubscriptionPrice));
        const earned = round(total - fee);
        if (fee > maxFee) maxFee = fee;
        return {
          ...platform,
          total,
          fee,
          earned,
          hasOverflow: fee > earned
        };
      });
      maxFee += (maxFee * 0.05); // add 5% buffer
      computed.forEach(platform => {
        platform.width = round((platform.fee / (maxFee || 1)) * 100);
        platform.actualPercent = round((platform.fee / (total || 1)) * 100); // not using for now
      });
      return computed;
    }
  },
  watch: {
    subscriberCount(val) {
      if ([null, ''].includes(val) || val < 1 || val > 1000) return;
      this.internalSubscriberCount = Number.isInteger(val) ? val : Math.round(val);
    },
    subscriptionPrice(val) {
      if ([null, ''].includes(val) || val < 10 || val > 1000) return;
      this.internalSubscriptionPrice = Number.isInteger(val) ? val : Math.round(val);
    }
  }
};
</script>

<style lang="scss" scoped>
.slider {
  @apply w-full appearance-none h-3 md:h-4 bg-gray-200 rounded-xl cursor-pointer;

  &::-webkit-slider-thumb {
    @apply appearance-none w-4 h-8 md:w-5 md:h-10 cursor-grab rounded-xl bg-fm-info;
    @apply active:cursor-grabbing;
  }

  &::-moz-range-thumb {
    @apply appearance-none w-4 h-8 md:w-5 md:h-10 cursor-grab rounded-xl -top-2 bg-fm-info border-0;
    @apply active:cursor-grabbing;
  }
}
</style>
