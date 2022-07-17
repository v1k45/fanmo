<template>
<div
  class="fm-marquee"
  :class="{ 'fm-marquee--with-overflow': hasOverflow }"
  @mouseover="isHovered = true;" @mouseleave="isHovered = false;">
  <div ref="content" class="fm-marquee__content">
    <slot></slot>
  </div>
</div>
</template>

<script>
import debounce from 'lodash/debounce';
export default {
  data() {
    return {
      hasOverflow: false,
      isHovered: false
    };
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
  methods: {
    handleIntersect(entries, observer, isIntersecting) {
      this.hasOverflow = isIntersecting;
    },
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
    }
  }
};
</script>
<style lang="scss">
.fm-marquee {
  @apply truncate;
}
.fm-marquee--with-overflow {
  @apply text-clip;
  .fm-marquee__content {
    @apply inline-block w-max pl-[100%] whitespace-nowrap;
    /* show the marquee just outside the paragraph */
    will-change: transform;
    animation: marquee 5s linear infinite;

    &:hover {
      animation-play-state: paused
    }
  }
}

@keyframes marquee {
  0% { transform: translate(0, 0); }
  100% { transform: translate(-100%, 0); }
}


/* Respect user preferences about animations */

@media (prefers-reduced-motion: reduce) {
  .fm-marquee__content {
    animation-iteration-count: 1;
    animation-duration: 0.01;
    /* instead of animation: none, so an animationend event is
     * still available, if previously attached.
     */
    width: auto;
    padding-left: 0;
  }
}
</style>
