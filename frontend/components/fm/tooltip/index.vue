<template>
<fm-popper
  ref="popper"
  v-slot="{ $reference, $popper, isVisible, show, hide }"
  v-bind="{
    placement,
    reference,
    custom: true,
    popperOptions: {
      offset: [0, 8],
      strategy: 'fixed',
      modifiers: [
        { name: 'arrow', options: { padding: 6 } }
      ]
    }
  }"
  :toggle-on-click="false" class="fm-tooltip">
  <div
    v-if="!reference" v-bind="$reference" class="fm-tooltip__reference" tabindex="0"
    @mouseover="localShow(show)" @mouseleave="localHide(hide)" @focus="localShow(show)" @blur="localHide(hide)">
    <slot></slot>
  </div>
  <div v-show="isVisible" v-bind="$popper" class="fm-tooltip__content-wrapper">
    <div class="fm-tooltip__arrow" data-popper-arrow></div>
    <div class="fm-tooltip__content">
      <slot name="content">{{ content }}</slot>
    </div>
  </div>
</fm-popper>
</template>

<script>
export default {
  props: {
    content: { type: String, default: '' },
    placement: { type: String, default: 'top' },
    disabled: { type: Boolean, default: false },
    delay: { type: Number, default: 500 },
    reference: { type: Element, default: null }
  },
  data() {
    return {
      timer: null,
      handlers: { // handlers for manual binding when using directive
        show: null,
        hide: null
      }
    };
  },
  watch: {
    reference: {
      immediate: true,
      handler(reference) {
        if (!reference) return;
        this.handlers.show = () => this.localShow(this.$refs.popper.show);
        this.handlers.hide = () => this.localHide(this.$refs.popper.hide);
        reference.addEventListener('mouseover', this.handlers.show);
        reference.addEventListener('mouseleave', this.handlers.hide);
        reference.addEventListener('focus', this.handlers.show);
        reference.addEventListener('blur', this.handlers.hide);
      }
    }
  },
  beforeDestroy() {
    if (!this.reference) return;
    this.reference.removeEventListener('mouseover', this.handlers.show);
    this.reference.removeEventListener('mouseleave', this.handlers.hide);
    this.reference.removeEventListener('focus', this.handlers.show);
    this.reference.removeEventListener('blur', this.handlers.hide);
  },
  methods: {
    localShow(show) {
      if (this.timer || this.disabled) return;
      if (!this.delay) return show();
      this.timer = setTimeout(() => {
        this.timer = null;
        show();
      }, this.delay);
    },
    localHide(hide) {
      clearTimeout(this.timer);
      this.timer = null;
      hide();
    }
  }
};
</script>

<style lang="scss">
.fm-tooltip {
  @apply relative overflow-visible;
}
.fm-tooltip__reference {
  @apply inline-block;
}
.fm-tooltip__content-wrapper {
  @apply absolute z-30 transition-opacity;
}
.fm-tooltip__arrow {
  &, &:before {
    @apply absolute bg-black box-border;
    height: 8px;
    width: 8px; // diagonal = ~14.14px
  }

  @apply invisible;

  &:before {
    content: '';
    @apply visible rotate-45;
  }
}
.fm-tooltip__content-wrapper {
  &[data-popper-placement^='top'] > .fm-tooltip__arrow {
    bottom: -3px;
  }

  &[data-popper-placement^='bottom'] > .fm-tooltip__arrow {
    top: -3px;
  }

  &[data-popper-placement^='left'] > .fm-tooltip__arrow {
    right: -3px;
  }

  &[data-popper-placement^='right'] > .fm-tooltip__arrow {
    left: -3px;
  }
}


.fm-tooltip__content {
  @apply bg-black text-white px-2 py-1 rounded text-sm shadow-lg max-h-[80vh] overflow-auto font-normal;
  @apply max-w-[85vw] sm:max-w-md;
}
</style>
