<template>
<div v-intersect.once="{ handler: handleIntersect, options }" :style="styles">
  <slot v-if="hasIntersected"></slot>
</div>
</template>

<script>
export default {
  props: {
    options: {
      type: Object,
      // For more information on types, navigate to:
      // https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
      default: () => ({
        root: undefined,
        rootMargin: undefined,
        threshold: 0
      })
    },
    minHeight: { type: [Number, String], default: null }
  },
  data() {
    return {
      hasIntersected: false
    };
  },
  computed: {
    styles() {
      if (this.hasIntersected || !this.minHeight) return '';
      let minHeight = this.minHeight;
      if (typeof minHeight === 'number' || !isNaN(Number(minHeight))) minHeight += 'px';
      return { minHeight };
    }
  },
  methods: {
    handleIntersect(entries, observer, isIntersecting) {
      if (this.hasIntersected) return;
      this.hasIntersected = isIntersecting;
    }
  }
};
</script>
