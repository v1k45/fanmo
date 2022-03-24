<template>
<button :type="nativeType" class="fm-button" :class="classes" v-on="$listeners">
  <slot></slot>
</button>
</template>

<script>

const BUTTON_TYPE_CLASSNAME_MAP = {
  primary: 'fm-button--primary',
  success: 'fm-button--success',
  error: 'fm-button--error',
  warning: 'fm-button--warning',
  info: 'fm-button--info',
  link: 'fm-button--link'
};

const BUTTON_SIZE_CLASSNAME_MAP = {
  lg: 'fm-button--lg'
};

export default {
  props: {
    nativeType: { type: String, default: 'button' },
    type: {
      type: String,
      default: '',
      validator: val => !val || !!BUTTON_TYPE_CLASSNAME_MAP[val]
    },
    block: { type: Boolean, default: false },
    size: { type: String, default: '', validator: val => !val || !!BUTTON_SIZE_CLASSNAME_MAP[val] }
  },
  computed: {
    classes() {
      return {
        [BUTTON_TYPE_CLASSNAME_MAP[this.type] || 'fm-button--default']: true,
        [BUTTON_SIZE_CLASSNAME_MAP[this.size] || '']: true,
        'fm-button--block': this.block
      };
    }
  }
};
</script>
<style lang="scss">
.fm-button {
  @apply px-8 py-3 text-sm leading-tight rounded-full transition duration-150 ease-in-out;
  @apply active:scale-95;
  &:focus {
    @apply outline-2 outline-offset-2;
  }
}
.fm-button--default {
  @apply bg-white py-2.5 border-fm-primary-100 border-2;
  @apply hover:bg-fm-primary-50 hover:text-fm-primary;
  @apply focus:bg-fm-primary-100 focus:text-fm-primary;
  @apply active:bg-fm-primary-100 active:text-fm-primary;
}
.fm-button--primary {
  @apply bg-fm-primary-500 text-white;
  @apply hover:bg-fm-primary-600;
  @apply focus:bg-fm-primary-600;
  @apply active:bg-fm-primary-700;
}
.fm-button--success {
  @apply bg-fm-success-600 text-white;
  @apply hover:bg-fm-success-700;
  @apply focus:bg-fm-success-700;
  @apply active:bg-fm-success-800;
}
.fm-button--error {
  @apply bg-fm-error-500 text-white;
  @apply hover:bg-fm-error-600;
  @apply focus:bg-fm-error-600;
  @apply active:bg-fm-error-700;
}
.fm-button--warning {
  @apply bg-fm-warning-500 text-white;
  @apply hover:bg-fm-warning-600;
  @apply focus:bg-fm-warning-600;
  @apply active:bg-fm-warning-700;
}
.fm-button--info {
  @apply bg-fm-info-500 text-white;
  @apply hover:bg-fm-info-600;
  @apply focus:bg-fm-info-600;
  @apply active:bg-fm-info-700;
}
.fm-button--link {
  @apply shadow-none bg-transparent border-0 text-fm-primary p-0;
  @apply hover:shadow-none hover:text-fm-primary-600 hover:bg-none;
  @apply focus:bg-none;
  @apply active:bg-none;
}

.fm-button[disabled] {
  @apply opacity-60 pointer-events-none;
}

.fm-button--block {
  @apply w-full;
}

.fm-button--lg {
  @apply py-3 text-base;
}
</style>
