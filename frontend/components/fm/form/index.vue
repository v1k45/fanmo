<template>
<form v-on="$listeners">
  <fm-alert v-if="globalErrors.length" type="error" class="mb-6">
    <div v-for="(error, index) in globalErrors" :key="index">{{ error.message }}</div>
  </fm-alert>

  <slot></slot>
</form>
</template>

<script>
export default {
  provide() {
    const vm = this;
    return {
      $form: {
        get errors() {
          return vm.errors;
        }
      }
    };
  },
  props: {
    errors: { type: Object, default: () => ({}) }
  },
  computed: {
    globalErrors() {
      const errors = this.errors || {};
      if (errors.non_field_errors) return errors.non_field_errors;
      else if (errors.detail) return [errors.detail];
      return [];
    }
  }
};
</script>
