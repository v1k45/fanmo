<template>
<div class="fm-alert" :class="classes">
  <!-- icon start -->
  <div v-if="showIcon" class="fm-alert__icon">
    <icon-info v-if="type === 'info'"></icon-info>
    <icon-alert-triangle v-else-if="type === 'warning'"></icon-alert-triangle>
    <icon-x-circle v-else-if="type === 'error'"></icon-x-circle>
    <icon-check-circle-2 v-else-if="type === 'success'"></icon-check-circle-2>
  </div>
  <!-- icon end -->

  <div class="fm-alert__content">
    <div v-if="$slots.title || title" class="fm-alert__title">
      <slot name="title">{{ title }}</slot>
    </div>
    <div v-if="$slots.default || message" class="fm-alert__text">
      <slot>{{ message }}</slot>
    </div>
  </div>
</div>
</template>

<script>
import { Info as IconInfo, AlertTriangle as IconAlertTriangle, XCircle as IconXCircle, CheckCircle2 as IconCheckCircle2 } from 'lucide-vue';

export default {
  components: {
    IconInfo,
    IconAlertTriangle,
    IconXCircle,
    IconCheckCircle2
  },
  props: {
    type: { type: String, default: 'info', validator: val => ['', 'info', 'warning', 'error', 'success'].includes(val) },
    title: { type: String, default: '' },
    message: { type: String, default: '' },
    clamped: { type: Boolean, default: false },
    showIcon: { type: Boolean, default: true }
  },
  computed: {
    classes() {
      const { type, clamped } = this;
      return {
        'fm-alert--info': type === 'info',
        'fm-alert--warning': type === 'warning',
        'fm-alert--error': type === 'error',
        'fm-alert--success': type === 'success',

        'fm-alert--clamped': clamped
      };
    }
  }
};
</script>
<style lang="scss">
.fm-alert {
  @apply bg-white border rounded-xl px-3 py-3 flex;

  & ~ .fm-alert {
    @apply mt-4;
  }
}
.fm-alert--clamped {
  @apply max-w-xl;
}
.fm-alert__icon {
  @apply self-baseline mr-3 flex-shrink-0;
  svg {
    @apply fill-current stroke-white h-6 w-6;
  }
}
.fm-alert__content {
  @apply flex-grow;
}
.fm-alert__title {
  @apply text-lg leading-tight font-bold mb-1;
}
.fm-alert--info {
  @apply bg-fm-info-50 border-fm-info-300;
  .fm-alert__icon {
    @apply text-fm-info;
  }
  .fm-alert__title {
    @apply text-fm-info-600;
  }
  .fm-alert__text{
    @apply text-fm-info-700;
  }
}
.fm-alert--warning {
  @apply bg-fm-warning-50 border-fm-warning-300;
  .fm-alert__icon {
    @apply text-fm-warning;
  }
  .fm-alert__title {
    @apply text-fm-warning-600;
  }
  .fm-alert__text{
    @apply text-fm-warning-800;
  }
}
.fm-alert--error {
  @apply bg-fm-error-50 border-fm-error-600;
  .fm-alert__icon {
    @apply text-fm-error;
  }
  .fm-alert__title {
    @apply text-fm-error-600;
  }
  .fm-alert__text{
    @apply text-fm-error-800;
  }
}
.fm-alert--success {
  @apply bg-fm-success-50 border-fm-success-400;
  .fm-alert__icon {
    @apply text-fm-success;
  }
  .fm-alert__title {
    @apply text-fm-success-600;
  }
  .fm-alert__text{
    @apply text-fm-success-900;
  }
}
</style>
