<template>
<div v-show="isActive" class="pt-6">
  <slot v-if="(lazy && !wasActiveBefore) ? isActive : true"></slot>
</div>
</template>
<script>
export default {
  inject: {
    $tabs: { default: () => ({ update() { throw new Error('Wrap it in fm-tab.'); } }) }
  },
  props: {
    id: { type: [String, Number], required: true },
    label: { type: [String, Number], default: '' },
    lazy: { type: Boolean, default: true }
  },
  data() {
    return {
      identity: 'fm-tabs-pane',
      wasActiveBefore: false
    };
  },
  computed: {
    isActive() {
      return this.$tabs && this.$tabs.activeTab === this.id;
    }
  },
  watch: {
    isActive: {
      handler(isActive) {
        if (isActive) this.wasActiveBefore = true;
      },
      immediate: true
    }
  },
  mounted() {
    this.$tabs.update();
  }
};
</script>
<style>

</style>
