<template>
<div>
  <slot v-bind="{ ...slotProps, show, hide }"></slot>
</div>
</template>

<script>
import { createPopper } from '@popperjs/core';

const registerClickOutside = function(el) {
  el.clickOutsideEvent = function(event) {
    if (el !== event.target && !el.contains(event.target)) {
      el.dispatchEvent(new MouseEvent('click-outside', event));
    }
  };
  document.body.addEventListener('pointerup', el.clickOutsideEvent);
};

const unregisterClickOutside = function(el) {
  document.body.removeEventListener('pointerup', el.clickOutsideEvent);
  delete el.clickOutsideEvent;
};

export default {
  props: {
    placement: { type: String, default: 'bottom' },
    toggleOnClick: { type: Boolean, default: true }
  },
  data() {
    return {
      slotProps: {
        $reference: { 'data-popper-id': 'reference' },
        $popper: { 'data-popper-id': 'popper' },
        isVisible: false
      },
      popper: null,
      state: {
        referenceEl: null,
        popperEl: null
      }
    };
  },
  computed: {
  },
  watch: {
    'slotProps.isVisible'(isVisible) {
      if (isVisible) this.show();
      else this.hide();
    },
    placement() {
      this.setOptions();
    },
    toggleOnClick() {
      this.init({ force: true });
    }
  },
  mounted() {
    this.init();
  },
  updated() {
    this.init();
  },
  beforeDestroy() {
    this.destroy();
  },
  methods: {
    getElements() {
      if (!this.$el) return { reference: null, popper: null };
      return {
        reference: this.$el.querySelector(`[data-popper-id="${this.slotProps.$reference['data-popper-id']}"]`),
        popper: this.$el.querySelector(`[data-popper-id="${this.slotProps.$popper['data-popper-id']}"]`)
      };
    },

    init({ force = false } = {}) {
      const { reference, popper } = this.getElements();
      if (!force) {
        if (this.state.referenceEl === reference && this.state.popperEl === popper) return;
        if (!reference || !popper) return;
      }
      this.popper = createPopper(reference, popper, {
        placement: this.placement,
        modifiers: []
      });
      this.state = {
        referenceEl: reference,
        popperEl: popper
      };

      const showEvents = ['focus'];
      const hideEvents = ['blur'];
      let useClickOutside = false;
      if (this.toggleOnClick) {
        registerClickOutside(this.$el);
        showEvents.push('click');
        useClickOutside = true;
      } else {
        showEvents.push('mouseenter');
        hideEvents.push('mouseleave');
      }

      showEvents.forEach((event) => {
        reference.addEventListener(event, () => {
          this.slotProps.isVisible = true;
        });
      });

      hideEvents.forEach((event) => {
        reference.addEventListener(event, () => {
          this.slotProps.isVisible = false;
        });
      });

      if (useClickOutside) this.$el.addEventListener('click-outside', () => {
        this.slotProps.isVisible = false;
      });
    },

    setOptions() {
      if (!this.popper) return;
      this.popper.setOptions(options => ({
        ...options,
        placement: this.placement
      }));
    },

    show() {
      if (!this.popper) return;
      // Enable the event listeners
      this.popper.setOptions((options) => ({
        ...options,
        modifiers: [
          ...options.modifiers,
          { name: 'eventListeners', enabled: true }
        ]
      }));
      this.slotProps.isVisible = true;
      // Update its position
      this.popper.update();
    },

    hide() {
      if (!this.popper) return;
      // Disable the event listeners
      this.popper.setOptions((options) => ({
        ...options,
        modifiers: [
          ...options.modifiers,
          { name: 'eventListeners', enabled: false }
        ]
      }));
      this.slotProps.isVisible = false;
    },

    destroy() {
      if (!this.popper) return;
      if (this.$el) unregisterClickOutside(this.$el);
      this.popper.destroy();
    }
  }
};
</script>
