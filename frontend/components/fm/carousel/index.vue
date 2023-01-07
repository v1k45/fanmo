<template>
<div class="fm-carousel">
  <div v-swipe class="fm-carousel__items" :class="height" @swiped="handleSwipe">
    <div class="fm-carousel-items-translator" :style="{ transform: `translateX(-${currentItem * 100}%)` }">
      <div
        v-for="(image, idx) in images" :key="idx" class="fm-carousel__item"
        :style="{ left: `${idx * 100}%` }" title="Click to view the full size image"
        @click="fullSize.isVisible = true">
        <img :src="getImage(image, 'medium')" :alt="`Image ${idx + 1}`">
      </div>
    </div>
    <button v-if="currentItem > 0" type="button" class="fm-carousel__previous" @click="navigate(-1)">
      <icon-chevron-left></icon-chevron-left>
    </button>
    <button v-if="currentItem < images.length - 1" type="button" class="fm-carousel__next" @click="navigate(1)">
      <icon-chevron-right></icon-chevron-right>
    </button>
    <div v-if="images.length > 1" class="fm-carousel__info">
      {{ currentItem + 1 }}/{{ images.length }}
    </div>
  </div>
  <div v-if="images.length > 1" class="px-5 py-2">
    <input v-model.number="currentItem" class="w-full" type="range" :min="0" :step="1" :max="images.length - 1">
  </div>
  <!-- temporarily disable image based nav, in future mix range + image nav -->
  <div v-if="false" class="fm-carousel__index">
    <button v-for="(image, idx) in images" :key="idx" type="button" class="fm-carousel__index-item" :class="{
      'fm-carousel__index-item--active': currentItem === idx
    }" @click="selectImage(idx)">
      <img :src="getImage(image, 'small')" :alt="`Image ${idx + 1}`">
    </button>
  </div>

  <fm-dialog v-model="fullSize.isVisible" dialog-class="!grow-0 md:mx-10" class="!items-center" custom-width no-padding>
    <img v-swipe :src="getImage(images[currentItem], 'full')" class="max-h-[90vh] rounded-lg" @swiped="handleSwipe">
    <button v-if="currentItem > 0" type="button" class="fm-carousel__previous" @click="navigate(-1)">
      <icon-chevron-left></icon-chevron-left>
    </button>
    <button v-if="currentItem < images.length - 1" type="button" class="fm-carousel__next" @click="navigate(1)">
      <icon-chevron-right></icon-chevron-right>
    </button>
    <div v-if="images.length > 1" class="fm-carousel__info">
      {{ currentItem + 1 }}/{{ images.length }}
    </div>
  </fm-dialog>
</div>
</template>

<script>
import debounce from 'lodash/debounce';
export default {
  props: {
    height: { type: String, default: 'h-[300px] lg:h-[450px]' },
    images: { type: Array, default: () => [] }
  },
  data() {
    return {
      currentItem: 0,
      fullSize: {
        isVisible: false,
        handler: null
      }
    };
  },
  created() {
    this.fullSize.handler = (evt) => this.handleKeyboardNav(evt);
    // eslint-disable-next-line nuxt/no-globals-in-created
    window.addEventListener('keydown', this.fullSize.handler);
  },
  beforeDestroy() {
    window.removeEventListener('keydown', this.fullSize.handler);
  },
  methods: {
    navigate(by) {
      this.currentItem = (this.currentItem + by) % (this.images.length);
    },
    handleSwipe: debounce(function(evt) {
      const direction = evt.detail.dir;
      if (direction === 'left') {
        if (this.currentItem < this.images.length - 1) this.navigate(1);
      } else if (direction === 'right') {
        if (this.currentItem > 0) this.navigate(-1);
      }
    }, 100, { leading: true, trailing: false }),
    handleKeyboardNav(evt) {
      if (!this.fullSize.isVisible) return;
      if (evt.key === 'Escape') {
        this.fullSize.isVisible = false;
      } else if (evt.key === 'ArrowRight') {
        if (this.currentItem < this.images.length - 1) this.navigate(1);
      } else if (evt.key === 'ArrowLeft') {
        if (this.currentItem > 0) this.navigate(-1);
      }
    },
    getImage(image, size) {
      if (typeof image !== 'object') return image;
      return image[size];
    },
    selectImage(idx) {
      if (this.currentItem === idx) {
        this.fullSize.isVisible = true;
      } else {
        this.currentItem = idx;
      }
    }
  }
};
</script>

<style lang="scss">
.fm-carousel {
}
.fm-carousel__items {
  @apply relative overflow-hidden;
}
.fm-carousel-items-translator {
  @apply h-full transition-transform;
}
.fm-carousel__item {
  @apply h-full w-full cursor-pointer absolute top-0;
  > img {
    @apply h-full w-full object-contain;
  }
}
.fm-carousel__previous,
.fm-carousel__next {
  @apply absolute rounded-full p-1 top-1/2 bg-white opacity-75 transition-all;
  @apply hover:opacity-100 active:scale-95;
}
.fm-carousel__previous {
  @apply left-4;
}
.fm-carousel__next {
  @apply right-4;
}
.fm-carousel__info {
  @apply absolute bottom-4 right-4 rounded-2xl px-4 text-sm bg-white bg-opacity-70;
}

.fm-carousel__index {
  @apply flex flex-wrap justify-center border border-t-0 bg-gray-100;
}
.fm-carousel__index-item {
  @apply relative w-[12.5%] sm:w-1/12 cursor-pointer;
  &:after {
    @apply block pb-[100%] relative;
    content: '';
  }
  > img {
    @apply h-full w-full absolute top-0 left-0 object-cover;
  }
}
.fm-carousel__index-item--active {
  @apply ring-2 ring-fm-primary scale-110 z-10;
}
</style>
