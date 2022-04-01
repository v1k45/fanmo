<template>
<div class="fm-tabs">
  <div class="fm-tabs__header" :class="{ 'fm-tabs__header--centered': centered }">
    <div v-for="tab in tabs" :key="tab.id" class="fm-tabs__header-item" :class="{
      'fm-tabs__header-item--active': tab.id === localValue
    }" @click="localValue = tab.id;">
      {{ tab.header }}
    </div>
  </div>
  <div class="fm-tabs__content">
    <slot></slot>
  </div>
</div>
</template>

<script>
import get from 'lodash/get';

export default {
  provide() {
    const vm = this;
    return {
      $tabs: {
        get activeTab() {
          return vm.localValue;
        },
        get update() {
          return vm.getTabs;
        }
      }
    };
  },
  props: {
    value: { type: [String, Number], default: '' },
    centered: { type: Boolean, default: false }
  },
  data() {
    return {
      tabs: []
    };
  },
  computed: {
    localValue: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('input', val);
      }
    }
  },
  methods: {
    getTabs() {
      const tabPanes = this.$slots.default
        .filter(compOrEl => get(compOrEl, 'componentInstance.identity') === 'fm-tabs-pane')
        .map(comp => comp.componentInstance);
      this.tabs = tabPanes.map(tab => ({
        id: tab.$props.id,
        header: tab.$props.label || tab.$props.id,
        content: tab.$slots.default || ''
      }));
    }
  }
};
</script>

<style lang="scss">
.fm-tabs {
}
.fm-tabs__header {
  @apply flex justify-center lg:justify-start max-w-full overflow-auto border-b;
}
.fm-tabs__header--centered {
  @apply justify-center lg:justify-center;
}
.fm-tabs__header-item {
  @apply px-4 sm:px-6 py-3 font-medium text-gray-400 text-lg cursor-pointer hover:bg-gray-100 rounded-t-lg select-none;
}
.fm-tabs__header-item--active {
  @apply relative text-black cursor-default hover:bg-inherit;
  &:after {
    content: '';
    @apply absolute left-0 bottom-0 w-full h-1 bg-fm-success;
  }
}
.fm-tabs__content {
  @apply pt-6;
}
</style>
