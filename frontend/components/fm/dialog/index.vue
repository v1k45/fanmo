<template>
<transition enter-active-class="animatecss-fadeIn" leave-to-class="animatecss-fadeOut" @after-leave="$emit('hidden')">
  <div v-show="isVisible" class="fm-dialog animatecss" :class="classes">
    <div class="fm-dialog__backdrop" @click="closeOnBackdropClick ? close() : () => {}"></div>
    <transition enter-active-class="animatecss-zoomIn" leave-to-class="animatecss-zoomOut">
      <div v-show="isVisible" class="fm-dialog__container animatecss" :class="dialogClass">
        <div v-if="$slots.header" class="fm-dialog__header">
          <slot name="header"></slot>
        </div>

        <button v-if="showClose" type="button" class="fm-dialog__close" @click="close">
          <icon-x class="h-5 w-5"></icon-x>
        </button>

        <div class="fm-dialog__content" :class="{ 'fm-dialog__content--no-padding': noPadding }">
          <slot></slot>
        </div>

        <div v-if="$slots.footer" class="fm-dialog__footer">
          <slot name="footer"></slot>
        </div>
      </div>
    </transition>
  </div>
</transition>
</template>

<script>
import { X as IconX } from 'lucide-vue';

export default {
  components: {
    IconX
  },
  props: {
    value: { type: Boolean, default: true },
    showClose: { type: Boolean, default: true },
    fullscreen: { type: Boolean, default: false },
    alert: { type: Boolean, default: false },
    closeOnBackdropClick: { type: Boolean, default: true },
    dialogClass: { type: String, default: '' },
    customWidth: { type: Boolean, default: false },
    noPadding: { type: Boolean, default: false }
  },
  computed: {
    isVisible: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('input', val);
      }
    },
    classes() {
      const { fullscreen, alert, customWidth } = this;
      return {
        'fm-dialog--alert': alert,
        'fm-dialog--clamped': !customWidth && !fullscreen,
        'fm-dialog--fullscreen': !customWidth && fullscreen
      };
    }
  },
  watch: {
    isVisible() {
      this.hideViewportScroll();
    }
  },
  mounted() {
    this.hideViewportScroll();
  },
  methods: {
    hideViewportScroll() {
      if (!document || !document.documentElement) return;
      if (this.isVisible) document.documentElement.classList.add('overflow-hidden');
      else if (this.$el && this.$el.parentElement && !this.$el.parentElement.closest('.fm-dialog')) document.documentElement.classList.remove('overflow-hidden');
    },
    close() {
      this.isVisible = false;
    }
  }
};
</script>
<style lang="scss">
.fm-dialog {
  @apply z-20 fixed top-0 left-0 h-screen w-screen flex items-end md:items-center justify-center;
  animation-duration: 200ms;
}
.fm-dialog__backdrop {
  @apply absolute top-0 left-0 h-full w-full bg-black bg-opacity-50;
}
.fm-dialog__container {
  @apply bg-white rounded-lg relative flex flex-col flex-grow overflow-hidden max-h-[90vh];
  animation-duration: 200ms;
}
.fm-dialog__header {
  @apply px-6 py-4 border-b text-xl text-black font-medium pr-9;
}
.fm-dialog__close {
  @apply absolute right-3 top-3 rounded-full flex-shrink-0 text-gray-500 hover:bg-gray-200 p-2 active:scale-90 transition-transform;
}
.fm-dialog__content {
  @apply px-6 py-4 flex-grow overflow-auto;
}
.fm-dialog__content--no-padding {
  @apply p-0;
}
.fm-dialog__footer {
  @apply px-6 py-3 border-t;
}


.fm-dialog--clamped > .fm-dialog__container {
  @apply max-w-xl;
}
.fm-dialog--fullscreen > .fm-dialog__container {
  @apply w-full h-full rounded-none max-h-[unset];
}


.fm-dialog--alert {
  @apply items-center;
  .fm-dialog__container {
    @apply flex-grow-0 w-[28rem] max-w-[90vw];
  }
}

</style>
