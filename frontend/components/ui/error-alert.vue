<template>
<div
  v-if="allErrors.length"
  class="alert alert-error">
  <div class="flex-1">
    <icon-slash class="w-6 h-6 mx-2 stroke-current"></icon-slash>
    <label
      v-for="(error, index) in allErrors"
      :key="index">{{ error.message }}</label>
  </div>
</div>
</template>

<script>
export default {
  name: 'ErrorAlert',
  props: {
    errors: { type: Object, default: () => ({}) }
  },
  computed: {
    allErrors() {
      const errors = this.errors || {};
      if (errors.non_field_errors) {
        return errors.non_field_errors;
      } else if (errors.detail) {
        return [errors.detail];
      }
      return [];
    }
  }
};
</script>
