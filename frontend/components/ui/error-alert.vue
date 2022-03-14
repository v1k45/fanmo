<template>
<fm-alert v-if="allErrors.length" type="error" class="mb-6">
  <div v-for="(error, index) in allErrors" :key="index">{{ error.message }}</div>
</fm-alert>
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
