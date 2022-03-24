<template>
<div>
  <div ref="content" :class="classes">
    <slot></slot>
  </div>
  <div class="text-right mt-1">
    <fm-button v-if="hasExtraText" type="link" class="inline-flex items-center" @click="toggleShowMore">
      <template v-if="showingMore">Show less <icon-chevron-up class="ml-1 inline-block h-em w-em"></icon-chevron-up></template>
      <template v-else>Show more <icon-chevron-down class="ml-1 inline-block h-em w-em"></icon-chevron-down></template>
    </fm-button>
  </div>
</div>
</template>

<script>
import debounce from 'lodash/debounce';
import { ChevronDown as IconChevronDown, ChevronUp as IconChevronUp } from 'lucide-vue';

const classMap = {
  1: 'line-clamp-1',
  2: 'line-clamp-2',
  3: 'line-clamp-3',
  4: 'line-clamp-4',
  5: 'line-clamp-5',
  6: 'line-clamp-6'
};
export default {
  components: {
    IconChevronDown,
    IconChevronUp
  },
  props: {
    lines: { type: [Number, String], default: 3, validator: val => !!classMap[val] }
  },
  data() {
    return {
      hasExtraText: false,
      skipExtraTextCompute: false,
      showingMore: false,
      observer: null
    };
  },
  computed: {
    classes() {
      return this.showingMore ? '' : (classMap[this.lines] || '');
    }
  },
  mounted() {
    this.observer = new ResizeObserver(debounce(entries => {
      if (this.skipExtraTextCompute) {
        this.skipExtraTextCompute = false;
        return;
      }
      this.computeHasExtraText();
    }, 250, {
      leading: true
    }));
    this.observer.observe(this.$refs.content);
  },
  beforeDestroy() {
    if (this.observer) this.observer.disconnect();
    this.observer = null;
  },
  methods: {
    async computeHasExtraText() {
      const el = this.$refs.content;
      if (!el) {
        this.hasExtraText = false;
        return;
      }
      let shouldSetShowingMore = false;
      if (this.showingMore) { // will probably regret not commenting what this is doing
        this.showingMore = false;
        shouldSetShowingMore = true;
        await this.$nextTick();
      }

      if (el.offsetHeight < el.scrollHeight || el.offsetWidth < el.scrollWidth) {
        this.hasExtraText = true;
      } else {
        this.hasExtraText = false;
      }
      if (shouldSetShowingMore) this.showingMore = true;
    },
    toggleShowMore() {
      this.skipExtraTextCompute = true;
      this.showingMore = !this.showingMore;
    }
  }
};
</script>

<style>

</style>
