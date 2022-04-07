<template>
<div class="fm-avatar" :class="size">
  <img v-if="src" :src="src" class="fm-avatar__image">
  <div
    v-else-if="initials"
    class="fm-avatar__initials"
    :class="color" :style="{ fontSize }">
    {{ initials }}
  </div>
  <img v-else src="~/assets/avatar-placeholder.png" class="fm-avatar__image">
</div>
</template>

<script>
const colorMap = [
  'bg-amber-500',
  'bg-blue-500',
  'bg-violet-500',
  'bg-fuchsia-500',
  'bg-pink-500',
  'bg-fm-primary',
  'bg-fm-success',
  'bg-fm-error',
  'bg-fm-warning'
];

export default {
  props: {
    src: { type: String, default: '' },
    name: { type: String, default: '' },
    username: { type: String, default: '' },
    size: { type: [String, Object, Array], default: 'w-8 h-8' }
  },
  data() {
    return {
      fontSize: '1em'
    };
  },
  computed: {
    initials() {
      const { name, username } = this;
      if (!name && !username) return '';

      const initials = (name || username).split(/[\s_.]/).map(str => str[0]).join('').toUpperCase();
      if (initials.length > 2) return `${initials[0]}${initials[initials.length - 1]}`;
      return initials;
    },
    color() {
      const { username } = this;
      if (!username) return 'bg-fm-primary';
      const colorIdx = username.split('').map(char => char.charCodeAt(0)).reduce((sum, curr) => sum + curr, 0) % colorMap.length;
      return colorMap[colorIdx];
    }
  },
  watch: {
    async size() {
      await this.$nextTick();
      this.calculateFontSize();
    }
  },
  mounted() {
    this.calculateFontSize();
  },
  methods: {
    calculateFontSize() {
      this.fontSize = '1em';
      if (!this.$el) return;
      const scaleDownBy = 0.4;
      const widthInPx = this.$el.clientWidth;
      if (widthInPx) this.fontSize = `${(widthInPx * scaleDownBy).toFixed(2)}px`;
    }
  }
};
</script>

<style lang="scss">
.fm-avatar {
  @apply rounded-full relative overflow-hidden;
}
.fm-avatar__image {
  @apply h-full w-full object-cover;
}
.fm-avatar__initials {
  @apply h-full w-full flex items-center justify-center select-none text-white;
}
</style>
