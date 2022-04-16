<template>
<div class="fm-input" :class="{ 'fm-input--error': !!computedError, 'fm-input--vertical': !horizontal, 'fm-input--horizontal': horizontal }">
  <!-- label start -->
  <label v-if="label || $slots.label" class="fm-input__label">
    <slot v-if="$slots.label" name="label"></slot>
    <template v-else-if="label">{{ label }}</template>
  </label>
  <!-- label end -->

  <slot name="after-label"></slot>

  <!-- field start -->
  <div class="relative">

    <!-- otp input start -->
    <template v-if="type === 'otp'">
      <fm-input-otp ref="input" v-model="model" :class="inputClass" :block="block" @filled="$emit('filled', $event)"></fm-input-otp>
    </template>
    <!-- otp input end -->

    <!-- rich input start -->
    <template v-else-if="type === 'rich'">
      <fm-editor ref="input" v-model="model" v-bind="props" :preset="preset" :class="inputClass"></fm-editor>
    </template>
    <!-- rich input end -->

    <!-- file input start -->
    <template v-else-if="type === 'file'">
      <fm-input-file ref="input" v-model="model" v-bind="{ ...$attrs, ...props }" :multiple="multiple" :class="inputClass"></fm-input-file>
    </template>
    <!-- file input end -->

    <!-- checkbox input start -->
    <template v-else-if="type === 'checkbox'">
      <label class="cursor-pointer inline-flex" :class="{ 'text-fm-primary': model }">
        <input ref="input" v-model="model" v-bind="$attrs" :value="nativeValue" type="checkbox" class="fm-input__input" :class="inputClass">
        <span v-if="$slots.default" class="ml-1">
          <slot></slot>
        </span>
      </label>
    </template>
    <!-- checkbox input end -->

    <!-- radio input start -->
    <template v-else-if="type === 'radio'">
      <label class="cursor-pointer inline-flex" :class="{ 'text-fm-primary': model === nativeValue }">
        <input ref="input" v-model="model" v-bind="$attrs" :value="nativeValue" type="radio" class="fm-input__input" :class="inputClass">
        <span v-if="$slots.default" class="ml-1">
          <slot></slot>
        </span>
      </label>
    </template>
    <!-- radio input end -->

    <!-- select start -->
    <template v-else-if="type === 'select'">
      <select ref="input" v-model="model" v-bind="$attrs" type="select" class="fm-input__input" :class="inputClass">
        <slot></slot>
      </select>
    </template>
    <!-- select end -->

    <!-- password input start -->
    <template v-else-if="type === 'password'">
      <input
        ref="input" v-model="model" v-bind="$attrs"
        :type="isPasswordVisible ? 'text' : 'password'" class="fm-input__input pr-8"
        :class="inputClass">
      <button
        class="absolute right-0 top-0 flex items-center justify-center h-full px-2" aria-hidden="true" type="button"
        :title="isPasswordVisible ? 'Hide password' : 'Show password'"
        @click="isPasswordVisible = !isPasswordVisible;">
        <icon-eye v-if="isPasswordVisible" :size="20"></icon-eye>
        <icon-eye-off v-else :size="20"></icon-eye-off>
      </button>
    </template>
    <!-- password input end -->

    <!-- textarea start -->
    <template v-else-if="type === 'textarea'">
      <!-- TODO: forward event listeners to other inputs eventually as the need arises -->
      <textarea ref="input" v-model="model" class="fm-input__input" :class="inputClass" v-bind="$attrs" v-on="listeners"></textarea>
    </template>
    <!-- textarea end -->

    <!-- default input start -->
    <template v-else>
      <div v-if="$slots.prepend" class="flex">
        <div class="fm-input__prepend">
          <slot name="prepend"></slot>
        </div>
        <input ref="input" v-model="model" v-bind="$attrs" :type="type" class="fm-input__input" :class="inputClass">
      </div>
      <input v-else ref="input" v-model="model" v-bind="$attrs" :type="type" class="fm-input__input" :class="inputClass">
    </template>
    <!-- default input end -->

  </div>
  <!-- field end -->

  <!-- error start -->
  <div v-if="computedError" class="fm-input__error">{{ computedError }}</div>
  <!-- field end -->

</div>
</template>

<script>
import get from 'lodash/get';
import { Eye as IconEye, EyeOff as IconEyeOff } from 'lucide-vue';

export default {
  components: {
    IconEye,
    IconEyeOff
  },
  inject: {
    $form: { default: () => ({ errors: {} }) }
  },
  inheritAttrs: false,
  props: {
    uid: { type: String, default: '' }, // for injecting errors if an input is inside fm-form. accepts path
    value: { type: [String, Number, Boolean, Array], default: '' },
    inputClass: { type: [String, Object, Array], default: '' },
    nativeValue: { type: [String, Number, Boolean], default: '' }, // for radios and checkboxes
    type: { type: String, default: 'text' },
    label: { type: String, default: '' },
    error: { type: String, default: '' },
    horizontal: { type: Boolean, default: false },
    block: { type: Boolean, default: false },
    preset: { type: String, default: undefined }, // for fm-editor (type=rich)
    multiple: { type: Boolean, default: false }, // for file input
    props: { type: Object, default: () => {} } // for any nested components like otp/editor
  },
  data() {
    return {
      isPasswordVisible: false
    };
  },
  computed: {
    model: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('input', val);
      }
    },
    listeners() {
      const RESERVED_EVENTS = ['input'];
      const listeners = { ...this.$listeners };
      RESERVED_EVENTS.forEach(evt => {
        delete listeners[evt];
      });
      return listeners;
    },
    computedError() {
      if (this.error) return this.error;
      let ret = get(this.$form.errors, this.uid);
      if (!this.uid || !ret || !ret.length) return '';
      ret = ret.map(err => (err.message || '')).join('. ');
      return ret;
    }
  },
  mounted() {
    const hasAutofocusSet = 'autofocus' in this.$attrs;
    if (hasAutofocusSet && this.$refs.input && this.$refs.input.focus) this.$refs.input.focus();
  },
  methods: {
    focus() {
      if (this.$refs.input && this.$refs.input.focus) this.$refs.input.focus();
    },
    blur() {
      if (this.$refs.input && this.$refs.input.blur) this.$refs.input.blur();
    }
  }
};
</script>

<style lang="scss">
.fm-input {
  @apply relative;
  .fm-input__input[type=email], .fm-input__input[type=number],
  .fm-input__input[type=text], .fm-input__input[type=password],
  .fm-input__input[type=url],
  textarea.fm-input__input, select.fm-input__input {
    @apply block w-full rounded-lg border-gray-300 border bg-white text-sm py-3;
    @apply focus:border-fm-primary;

    &::placeholder {
      @apply text-gray-400;
    }

    &[disabled] {
      @apply cursor-not-allowed bg-gray-50 text-gray-400;
    }
  }

  .fm-input__input[type=checkbox], .fm-input__input[type=radio] {
    @apply w-5 h-5 rounded border-gray-300 border cursor-pointer mr-1;
    @apply checked:bg-fm-primary checked:border-0;
    @apply focus:ring-1;
  }

  .fm-input__input[type=radio] {
    @apply rounded-full mt-[2px];
  }

}
.fm-input__label {
  @apply block mb-2 text-black;
}
.fm-input__error {
  @apply absolute text-fm-error text-xs left-0 top-full mt-1 max-w-full;
}
.fm-input--error {
  .fm-input__label {
    @apply text-fm-error;
  }
  .fm-input__input[type=email], .fm-input__input[type=number],
  .fm-input__input[type=text], .fm-input__input[type=password],
  .fm-input__input[type=url], .fm-input__input[type=checkbox],
  .fm-input__input[type=radio],
  textarea.fm-input__input, select.fm-input__input {
    @apply border-fm-error;
    @apply focus:border-fm-error focus:ring-fm-error;
  }
}

.fm-input__prepend {
  @apply flex items-center px-5 rounded-l-lg bg-gray-100 border border-gray-300 border-r-0;
  + .fm-input__input[type] {
    @apply rounded-l-none;
  }
}


.fm-input--vertical + .fm-input--vertical {
  @apply mt-6;
}

.fm-input--horizontal {
  @apply inline-block;

  & + .fm-input--horizontal {
    @apply ml-6;
  }
}
</style>
