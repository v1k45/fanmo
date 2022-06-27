<template>
<div class="mt-6 lg:my-12 lg:mx-4">

  <!-- header start -->
  <div class="container sm:pl-0">
    <div class="text-2xl text-black font-bold">Dashboard</div>
    <div class="mt-1 text-gray-600">View and manage members, review transaction history and manage membership tiers.</div>
  </div>
  <!-- header end -->

  <!-- stats and chart start -->
  <div class="mt-5 pb-12 rounded-xl border bg-white">
    <div class="md:px-8 container">

      <!-- heading + period selector start -->
      <div class="flex flex-wrap relative">
        <div class="text-xl text-black font-medium mr-auto mt-6">Recent trends</div>

        <div class="mt-3 sm:mt-6 text-sm sm:text-base">
          <fm-input v-model="form.period" native-value="week" type="radio" name="data_period" horizontal :disabled="isAnalyticsLoading">Last 7 days</fm-input>
          <fm-input v-model="form.period" native-value="month" type="radio" name="data_period" horizontal :disabled="isAnalyticsLoading">Last 30 days</fm-input>
          <fm-input v-model="form.period" native-value="lifetime" type="radio" name="data_period" horizontal :disabled="isAnalyticsLoading">Lifetime</fm-input>

        </div>
        <div v-if="isAnalyticsLoading" class="absolute right-0 top-full text-gray-500 text-sm">Loading...</div>
      </div>
      <!-- heading + period selector end -->

      <!-- stats start -->
      <div v-if="analytics" class="flex xl:space-x-12 flex-wrap">

        <!-- stats: new members start -->
        <div class="w-1/2 sm:w-1/3 xl:w-[unset] text-sm md:text-base mt-6">
          <div class="text-gray-500">New members</div>
          <div class="flex items-end">
            <div class="text-lg md:text-xl font-medium">{{ parseInt(analytics.new_member_count.current) }}</div>

            <!-- delta start -->
            <div :class="{
              'text-fm-success-600': Number(analytics.new_member_count.percent_change) > 0,
              'text-fm-error': Number(analytics.new_member_count.percent_change) < 0,
              'text-gray-400': Number(analytics.new_member_count.percent_change) === 0
            }" class="ml-2 text-sm font-bold">
              {{ Number(analytics.new_member_count.percent_change) }}%
              <template v-if="Number(analytics.new_member_count.percent_change) > 0">&uarr;</template>
              <template v-else-if="Number(analytics.new_member_count.percent_change) < 0">&darr;</template>
              <template v-else>&approx;</template>
            </div>
            <!-- delta end -->
          </div>
        </div>
        <!-- stats: new members end -->

        <!-- stats: donation earnings start -->
        <div class="w-1/2 sm:w-1/3 xl:w-[unset] text-sm md:text-base mt-6">
          <div class="text-gray-500">Donation earnings</div>
          <div class="flex items-end">
            <div class="text-lg md:text-xl font-medium">{{ $currency(analytics.total_donation_amount.current) }}</div>
            <!-- delta start -->
            <div :class="{
              'text-fm-success-600': Number(analytics.total_donation_amount.percent_change) > 0,
              'text-fm-error': Number(analytics.total_donation_amount.percent_change) < 0,
              'text-gray-400': Number(analytics.total_donation_amount.percent_change) === 0
            }" class="ml-2 text-sm font-bold">
              {{ Number(analytics.total_donation_amount.percent_change) }}%
              <template v-if="Number(analytics.total_donation_amount.percent_change) > 0">&uarr;</template>
              <template v-else-if="Number(analytics.total_donation_amount.percent_change) < 0">&darr;</template>
              <template v-else>&approx;</template>
            </div>
            <!-- delta end -->
          </div>
        </div>
        <!-- stats: donation earnings end -->

        <!-- stats: membership earnings start -->
        <div class="w-1/2 sm:w-1/3 xl:w-[unset] text-sm md:text-base mt-6">
          <div class="text-gray-500">Membership earnings</div>
          <div class="flex items-end">
            <div class="text-lg md:text-xl font-medium">{{ $currency(analytics.total_membership_amount.current) }}</div>
            <!-- delta start -->
            <div :class="{
              'text-fm-success-600': Number(analytics.total_membership_amount.percent_change) > 0,
              'text-fm-error': Number(analytics.total_membership_amount.percent_change) < 0,
              'text-gray-400': Number(analytics.total_membership_amount.percent_change) === 0
            }" class="ml-2 text-sm font-bold">
              {{ Number(analytics.total_membership_amount.percent_change) }}%
              <template v-if="Number(analytics.total_membership_amount.percent_change) > 0">&uarr;</template>
              <template v-else-if="Number(analytics.total_membership_amount.percent_change) < 0">&darr;</template>
              <template v-else>&approx;</template>
            </div>
            <!-- delta end -->
          </div>
        </div>
        <!-- stats: membership earnings end -->

        <!-- stats: total earnings start -->
        <div class="w-1/2 sm:w-1/3 xl:w-[unset] text-sm md:text-base mt-6">
          <div class="text-gray-500">Total earnings</div>
          <div class="flex items-end">
            <div class="text-lg md:text-xl font-medium">{{ $currency(analytics.total_payment_amount.current) }}</div>
            <!-- delta start -->
            <div :class="{
              'text-fm-success-600': Number(analytics.total_payment_amount.percent_change) > 0,
              'text-fm-error': Number(analytics.total_payment_amount.percent_change) < 0,
              'text-gray-400': Number(analytics.total_payment_amount.percent_change) === 0
            }" class="ml-2 text-sm font-bold">
              {{ Number(analytics.total_payment_amount.percent_change) }}%
              <template v-if="Number(analytics.total_payment_amount.percent_change) > 0">&uarr;</template>
              <template v-else-if="Number(analytics.total_payment_amount.percent_change) < 0">&darr;</template>
              <template v-else>&approx;</template>
            </div>
            <!-- delta end -->
          </div>
        </div>
        <!-- stats: total earnings end -->

      </div>
      <!-- stats end -->

      <!-- chart start -->
      <div ref="chart" class="mt-8"></div>
      <!-- chart end -->

    </div>
  </div>
  <!-- stats and chart end -->

  <!-- activity start -->
  <div class="mt-5 pb-12 rounded-xl border bg-white">
    <div class="md:px-8 container">
      <div class="text-xl mt-6 mb-6 text-black font-medium mr-auto">Recent activity</div>

      <!-- activity list start -->
      <fm-timeline v-if="activities && activities.results.length">
        <fm-timeline-item v-for="activity in activities.results" :key="activity.id"
          :tail-class="['bg-gray-300' || activityTypeMap[activity.type].bgClass, 'w-[2px]']">
          <template #icon>
            <div
              class="rounded-full bg-white relative h-8 w-8 flex justify-center items-center"
              :class="[activityTypeMap[activity.type].bgClass, 'text-white']">
              <component :is="activityTypeMap[activity.type].icon" class="h-4 w-4 stroke-2"></component>
            </div>
          </template>
          <div class="mb-4">
            <div class="text-gray-600">
              <span class="font-medium text-black">{{ activity.fan_user.display_name }}</span>{{ activity.message.replace(activity.fan_user.display_name, '') }}
            </div>
            <div class="text-sm text-gray-500">
              {{ dayjs(activity.created_at).fromNow() }}
            </div>
          </div>
        </fm-timeline-item>
      </fm-timeline>
      <!-- activity list end -->

      <!-- activity no-data start -->
      <div v-else-if="activities && !activities.count" class="h-52 px-4 bg-gray-100 rounded-xl mx-auto flex justify-center flex-col items-center">
        <div class="opacity-60 text-center">
          <icon-history :size="48" class="mx-auto mb-3"></icon-history>
          <div>
            Recent activity by your fans will appear here. <br>
            Share your Fanmo page with your fans to get started.
          </div>
        </div>
      </div>
      <!-- activity no-data end -->

      <!-- activity load next start -->
      <div v-if="activities && activities.next" class="text-center mt-4">
        <fm-button :loading="isNextActivitiesLoading" @click="loadNextActivitiesLocal">Load more</fm-button>
      </div>
      <!-- activity load next end -->

    </div>
  </div>
  <!-- activity end -->

</div>
</template>

<script>
import ApexCharts from 'apexcharts';
import { mapActions, mapState } from 'vuex';
import { UserPlus, UserX, UserCog, Coins, MessageSquare, MessageCircle, UserCheck } from 'lucide-vue';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import get from 'lodash/get';
import { toCurrency } from '~/utils';

dayjs.extend(relativeTime);


// chart options
const options = () => ({
  series: [],
  chart: {
    type: 'area',
    height: 350,
    stacked: true,
    toolbar: {
      show: true,
      tools: {
        download: false,
        selection: true,
        zoom: true,
        zoomin: true,
        zoomout: false,
        pan: false,
        reset: true
      }
    }
  },
  colors: ['#008FFB', '#00E396', '#CED4DC'],
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  fill: {
    type: 'gradient',
    gradient: {
      opacityFrom: 1,
      opacityTo: 1
    }
  },
  legend: {
    position: 'top',
    horizontalAlign: 'left'
  },
  tooltip: {
    y: {
      formatter(value, { series, dataPointIndex }) {
        const sum = series[0][dataPointIndex] + series[1][dataPointIndex];
        if (sum === 0 || value === 0 || value === sum) return toCurrency(value);
        return `${toCurrency(value)} of ${toCurrency(sum)}`;
      }
    }
  },
  yaxis: {
    labels: {
      formatter(value) {
        return toCurrency(value);
      }
    }
  },
  xaxis: {
    type: 'datetime'
  },
  noData: {
    text: undefined
  }
});

export default {
  auth: true,
  layout: 'with-sidebar',
  data() {
    return {
      get,
      dayjs,
      chartInstance: null,
      form: {
        period: 'week'
      },
      activityTypeMap: {
        new_membership: {
          icon: UserPlus,
          bgClass: 'bg-fm-success',
          borderClass: 'border-fm-success',
          textClass: 'text-fm-success'
        },
        membership_update: {
          icon: UserCog,
          bgClass: 'bg-fm-info',
          borderClass: 'border-fm-info',
          textClass: 'text-fm-info'
        },
        membership_stop: {
          icon: UserX,
          bgClass: 'bg-fm-error',
          borderClass: 'border-fm-error',
          textClass: 'text-fm-error'
        },
        donation: {
          icon: Coins,
          bgClass: 'bg-fm-success',
          borderClass: 'border-fm-success',
          textClass: 'text-fm-success'
        },
        comment: {
          icon: MessageSquare,
          bgClass: 'bg-fm-info',
          borderClass: 'border-fm-info',
          textClass: 'text-fm-info'
        },
        comment_reply: {
          icon: MessageCircle,
          bgClass: 'bg-fm-info',
          borderClass: 'border-fm-info',
          textClass: 'text-fm-info'
        },
        follower: {
          icon: UserCheck,
          bgClass: 'bg-fm-info',
          borderClass: 'border-fm-info',
          textClass: 'text-fm-info'
        }
      },
      isAnalyticsLoading: false,
      isNextActivitiesLoading: false
    };
  },
  head: {
    title: 'Dashboard'
  },
  computed: {
    ...mapState('users', ['analytics', 'activities'])
  },
  watch: {
    'form.period'() {
      this.loadAnalyticsLocal();
    }
  },
  created() {
    this.loadAnalyticsLocal();
    this.loadActivities();
  },
  mounted() {
    this.chartInstance = new ApexCharts(this.$refs.chart, options());
    this.chartInstance.render();
    this.$watch(function() {
      if (!this.analytics) return this.analytics;
      const arr = [
        ...this.analytics.total_donation_amount.series,
        ...this.analytics.total_membership_amount.series
      ];
      return JSON.stringify(arr);
    }, function() {
      if (!this.analytics) {
        this.$refs.chart.replaceChildren();
        return;
      }
      this.chartInstance.updateSeries([
        {
          name: 'Membership earnings',
          data: this.analytics.total_membership_amount.series
        },
        {
          name: 'Donation earnings',
          data: this.analytics.total_donation_amount.series
        }
      ]);
    }, {
      immediate: true
    });
  },
  methods: {
    ...mapActions('users', ['loadAnalytics', 'loadActivities', 'loadNextActivities']),
    async loadNextActivitiesLocal() {
      this.isNextActivitiesLoading = true;
      await this.loadNextActivities();
      this.isNextActivitiesLoading = false;
    },
    async loadAnalyticsLocal() {
      this.isAnalyticsLoading = true;
      await this.loadAnalytics(this.form.period);
      this.isAnalyticsLoading = false;
    }
  }
};
</script>
