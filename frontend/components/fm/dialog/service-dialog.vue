<template>
<fm-dialog
  v-model="isVisible" class="fm-service-dialog" :class="classes"
  alert :show-close="false" require-explicit-close
  @hidden="$emit('closed')">
  <div class="flex">
    <!-- icon start -->
    <div v-if="type" class="fm-service-dialog__icon">
      <icon-info v-if="type === 'info'"></icon-info>
      <icon-alert-triangle v-else-if="type === 'warning'"></icon-alert-triangle>
      <icon-alert-triangle v-else-if="type === 'error'"></icon-alert-triangle>
      <icon-check-circle-2 v-else-if="type === 'success'"></icon-check-circle-2>
    </div>
    <!-- icon end -->
    <div>
      <template v-if="title">
        <div v-if="html" class="fm-service-dialog__title" v-html="title"></div>
        <div v-else class="fm-service-dialog__title">{{ title }}</div>
      </template>
      <div v-if="html" v-html="message"></div>
      <div v-else>{{ message }}</div>
    </div>

  </div>
  <div class="mt-4 text-right">
    <fm-button v-if="dialogType === 'alert'" @click="ok">{{ okButtonText }}</fm-button>

    <template v-if="dialogType === 'confirm'">
      <fm-button @click="cancel">{{ cancelButtonText }}</fm-button>
      <fm-button :type="type || 'primary'" @click="ok">{{ okButtonText }}</fm-button>
    </template>
  </div>
</fm-dialog>
</template>
<script>
export default {
  props: {
    dialogType: { type: String, default: 'alert', validator: val => ['alert', 'confirm'].includes(val) },
    type: { type: String, default: '', validator: val => ['', 'info', 'warning', 'error', 'success'].includes(val) },
    title: { type: String, default: '' },
    message: { type: String, default: '' },
    html: { type: Boolean, default: false },

    okButtonText: { type: String, default: 'OK' },
    cancelButtonText: { type: String, default: 'Cancel' }
  },
  data() {
    return {
      isVisible: false
    };
  },
  computed: {
    classes() {
      const { type } = this;
      return {
        'fm-service-dialog--info': type === 'info',
        'fm-service-dialog--warning': type === 'warning',
        'fm-service-dialog--error': type === 'error',
        'fm-service-dialog--success': type === 'success'
      };
    }
  },
  mounted() {
    this.isVisible = true;
  },
  methods: {
    ok() {
      this.$emit('ok');
      this.isVisible = false;
    },
    cancel() {
      this.$emit('cancel');
      this.isVisible = false;
    }
  }
};
</script>
<style lang="scss">
.fm-service-dialog .fm-dialog__content {
  @apply pt-6;
}
.fm-service-dialog__icon {
  @apply self-baseline mr-3 rounded-full;
  svg {
    @apply fill-current stroke-white h-10 w-10;
  }
}

.fm-service-dialog__title {
  @apply text-lg font-medium mb-1;
}

.fm-service-dialog--info {
  .fm-service-dialog__icon,
  .fm-service-dialog__title {
    @apply text-fm-info;
  }
}
.fm-service-dialog--warning {
  .fm-service-dialog__icon {
    @apply text-fm-warning;
  }
  .fm-service-dialog__title {
    @apply text-fm-warning-600;
  }
}
.fm-service-dialog--error {
  .fm-service-dialog__icon,
  .fm-service-dialog__title {
    @apply text-fm-error;
  }
}
.fm-service-dialog--success {
  .fm-service-dialog__icon {
    @apply text-fm-success;
  }
  .fm-service-dialog__title {
    @apply text-fm-success-600;
  }
}
</style>
