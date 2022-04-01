<template>
<div>
  <div
    ref="content"
    :style="styles"
    class="transition-[max-height] max-h-max"
    :class="{
      'fm-read-more-height__content--hidden': hasOverflow && !showingMore
    }">
    <slot></slot>
  </div>
  <div class="text-right">
    <fm-button
      v-if="hasOverflow"
      type="link"
      class="inline-flex items-center"
      @click="toggleShowMore">
      <template v-if="showingMore">
        Show less
        <icon-chevron-up class="ml-1 inline-block h-em w-em"></icon-chevron-up>
      </template>
      <template v-else>
        Show more
        <icon-chevron-down
          class="ml-1 inline-block h-em w-em"></icon-chevron-down>
      </template>
    </fm-button>
  </div>
</div>
</template>

<script>
import debounce from 'lodash/debounce';
import {
  ChevronDown as IconChevronDown,
  ChevronUp as IconChevronUp
} from 'lucide-vue';

export default {
  components: {
    IconChevronDown,
    IconChevronUp
  },
  props: {
    maxHeight: { type: [Number, String], default: null }
  },
  data() {
    return {
      hasOverflow: false,
      skipExtraTextCompute: false,
      showingMore: false,
      observer: null
    };
  },
  computed: {
    styles() {
      if (!this.maxHeight || this.showingMore) return {};
      return {
        maxHeight:
          (typeof this.maxHeight === 'number' || Number.isFinite(parseFloat(this.maxHeight)))
            ? this.maxHeight + 'px'
            : this.maxHeight
      };
    }
  },
  mounted() {
    this.observer = new ResizeObserver(
      debounce(
        entries => {
          if (this.skipExtraTextCompute) {
            this.skipExtraTextCompute = false;
            return;
          }
          this.computeHasOverflow();
        },
        250,
        {
          leading: true
        }
      )
    );
    this.observer.observe(this.$refs.content);
  },
  beforeDestroy() {
    if (this.observer) this.observer.disconnect();
    this.observer = null;
  },
  methods: {
    async computeHasOverflow() {
      const el = this.$refs.content;
      if (!el) {
        this.hasOverflow = false;
        return;
      }
      let shouldSetShowingMore = false;
      if (this.showingMore) {
        // will probably regret not commenting what this is doing
        this.showingMore = false;
        shouldSetShowingMore = true;
        await this.$nextTick();
      }

      if (
        el.offsetHeight < el.scrollHeight ||
        el.offsetWidth < el.scrollWidth
      ) {
        this.hasOverflow = true;
      } else {
        this.hasOverflow = false;
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

<style lang="scss">
.fm-read-more-height__content--hidden {
  @apply overflow-hidden relative transition-[max-height];
  &:after {
    content: '';
    @apply absolute bottom-0 left-0 pointer-events-none z-[1] w-full h-8;
    background-image : linear-gradient(
      to bottom,
      transparent,
      white 90%
    );
  }
}
</style>
