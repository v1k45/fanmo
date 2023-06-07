<template>
<div>
  <div class="flex items-start space-x-3">
    <div class="font-semibold">
      <component :is="`icon-${icon}`"></component>
    </div>
    <div class="flex-grow">
      <div class="font-semibold">{{ title }}</div>
      <div class="text-sm text-gray-500">{{ description }}</div>
    </div>
    <div>
      <fm-button size="sm" @click="$emit('input', !value);">
        <div class="flex space-x-1 items-center">
          <icon-chevrons-up-down class="h-em w-em"></icon-chevrons-up-down>
          <span>{{ value ? "Hide" : "Show" }}</span>
        </div>
      </fm-button>
    </div>
  </div>
  <div v-show="value" class="mt-4">
    <slot></slot>
  </div>
</div>
</template>

<script>
export default {
  props: {
    value: {
      type: Boolean,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    }
  }
};
</script>

<style>

</style>
