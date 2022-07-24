<template>
<!--
  Stripped down version of fm-input only for rich editor. The purpose is to avoid auto-registering
  and including this in every page because rich editor comes with heavy dependency overhead.
  Any page that needs to use this would have to explicitly add an import for it.
 -->
<div class="fm-input" :class="{
  'fm-input--error': !!computedError,
  'fm-input--vertical': !horizontal,
  'fm-input--horizontal': horizontal
}">
  <!-- label start -->
  <label v-if="label || $slots.label" class="fm-input__label">
    <slot v-if="$slots.label" name="label"></slot>
    <template v-else-if="label">{{ label }}</template>
  </label>
  <!-- label end -->

  <!-- description start -->
  <div v-if="description || $slots.description" class="fm-input__description">
    <slot v-if="$slots.description" name="description"></slot>
    <template v-else-if="description">{{ description }}</template>
  </div>
  <!-- description end -->

  <slot name="after-label"></slot>

  <!-- field start -->
  <div class="relative">

    <!-- rich input start -->
    <fm-editor ref="input" v-model="model" v-bind="props" :preset="preset" :class="inputClass"></fm-editor>
    <!-- rich input end -->

  </div>
  <!-- field end -->

  <!-- error start -->
  <div v-if="computedError" class="fm-input__error">{{ computedError }}</div>
  <!-- field end -->

</div>
</template>

<script>
import get from 'lodash/get';
import FmEditor from '~/components/fm/editor/index.vue';

export default {
  components: {
    FmEditor
  },
  inject: {
    $form: { default: () => ({ errors: {} }) }
  },
  inheritAttrs: false,
  props: {
    uid: { type: String, default: '' }, // for injecting errors if an input is inside fm-form. accepts path
    value: { type: [String, Number, Boolean, Array, File], default: '' },
    inputClass: { type: [String, Object, Array], default: '' },
    label: { type: String, default: '' },
    description: { type: String, default: '' },
    error: { type: String, default: '' },
    horizontal: { type: Boolean, default: false },
    preset: { type: String, default: undefined }, // for fm-editor
    props: { type: Object, default: () => {} } // for any nested components like otp/editor
  },
  data() {
    return {};
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
