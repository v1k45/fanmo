<template>
<div ref="content" class="fm-markdown-styled">
  <slot></slot>
  <fm-dialog v-if="images.length" v-model="dialogVisible" dialog-class="!grow-0 md:mx-10" class="!items-center" custom-width no-padding>

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
  data() {
    return {
      images: [],
      currentItem: 0,
      dialogVisible: false,
      handler: null
    };
  },
  created() {
    this.handler = (evt) => this.handleKeyboardNav(evt);
    // eslint-disable-next-line nuxt/no-globals-in-created
    window.addEventListener('keydown', this.handler);
  },
  mounted() {
    this.addImgEventListeners();
  },
  beforeDestroy() {
    this.removeImgEventListeners();
    window.removeEventListener('keydown', this.handler);
  },
  methods: {
    getImage(image, size) {
      if (!image.includes('/imageproxy/')) return image;
      return image.replace('medium', size);
    },
    selectImage(idx) {
      if (this.currentItem === idx) {
        this.dialogVisible = true;
      } else {
        this.currentItem = idx;
      }
    },
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
      if (!this.dialogVisible) return;
      if (evt.key === 'Escape') {
        this.dialogVisible = false;
      } else if (evt.key === 'ArrowRight') {
        if (this.currentItem < this.images.length - 1) this.navigate(1);
      } else if (evt.key === 'ArrowLeft') {
        if (this.currentItem > 0) this.navigate(-1);
      }
    },
    addImgEventListeners() {
      const imgTags = this.$refs.content.querySelectorAll('img');
      imgTags.forEach((img) => {
        this.images.push(img.src);
        img.addEventListener('click', this.handleImgClick);
      });
    },
    removeImgEventListeners() {
      const imgTags = this.$refs.content.querySelectorAll('img');
      imgTags.forEach((img) => {
        img.removeEventListener('click', this.handleImgClick);
      });
    },
    handleImgClick(event) {
      const imgIdx = this.images.indexOf(event.target.src);
      if (imgIdx !== -1) {
        this.currentItem = imgIdx;
        this.dialogVisible = true;
      }
    }
  }
};
</script>

<style lang="scss">
.fm-markdown-styled {
  font-size: 1em;
  line-height: 1.5;
  word-wrap: break-word;

  .lucide-icon {
    display: inline-block;
    overflow: visible;
    vertical-align: text-bottom;
    fill: currentColor;
  }

  a {
    background-color: transparent;
    text-decoration: none;

    &:active, &:hover {
      outline-width: 0;
      text-decoration: underline;
    }

    :not([href]) {
      color: inherit;
      text-decoration: none;
    }
  }

  b, strong {
    font-weight: 600;
  }

  small {
    font-size: 90%;
  }

  img {
    @apply mx-auto;
  }

  code,
  kbd,
  pre,
  samp {
    font-family: monospace,monospace;
    font-size: 1em;
  }

  hr {
    box-sizing: content-box;
    overflow: hidden;
    background: transparent;
    border-bottom: 1px solid hsla(210,18%,87%,1);
    height: .25em;
    padding: 0;
    margin: 24px 0;
    background-color: #d0d7de;
    border: 0;
    &:before {
      display: table;
      content: "";
    }
    &:after {
      display: table;
      clear: both;
      content: "";
    }
  }

  h3 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 500;
    line-height: 1.25;
    font-size: 1.25em;
  }

  p {
    margin-top: 0;
    margin-bottom: 10px;
    &:last-child {
      margin-bottom: 0;
    }
  }

  blockquote {
    @apply pr-2 py-3 pl-4 border-l-4 bg-gray-100 border-fm-primary rounded-r-lg;
    > :first-child {
      margin-top: 0;
    }

    > :last-child {
      margin-bottom: 0;
    }
  }

  ul {
    list-style-type: disc;
  }
  ol {
    list-style-type: decimal;
  }

  ul,
  ol {
    margin-top: 0;
    margin-bottom: 0;
    padding-left: 2em;

    ol {
      list-style-type: lower-roman;
    }
    ul, ol {
      margin-top: 0;
      margin-bottom: 0;

      ol {
        list-style-type: lower-alpha;
      }
    }
  }

  li {
    > p {
      margin: 0;
    }
    + li {
      margin-top: .25em;
    }
  }

  code {
    font-family: ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace;
    font-size: 12px;
    padding: .2em .4em;
    margin: 0;
    font-size: 85%;
    background-color: rgba(175,184,193,0.2);
    border-radius: 6px;

    br {
      display: none;
    }
  }

  pre {
    margin-top: 0;
    margin-bottom: 0;
    font-family: ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace;
    word-wrap: normal;
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    background-color: #f6f8fa;
    border-radius: 6px;

    code {
      font-size: 100%;
    }

    > code {
      padding: 0;
      margin: 0;
      word-break: normal;
      white-space: pre;
      background: transparent;
      border: 0;
      display: inline;
      max-width: auto;
      overflow: visible;
      line-height: inherit;
      word-wrap: normal;
      background-color: transparent;
    }
  }

  > *:first-child {
    margin-top: 0 !important;
  }

  > *:last-child {
    margin-bottom: 0 !important;
  }

  p,
  blockquote,
  ul,
  ol,
  pre {
    margin-top: 0;
    margin-bottom: 16px;
  }

  .highlight {
    margin-bottom: 16px;

    pre {
      margin-bottom: 0;
      word-break: normal;
    }
  }

}

.fm-markdown-styled pre code {
  display: inline;
  max-width: auto;
  padding: 0;
  margin: 0;
  overflow: visible;
  line-height: inherit;
  word-wrap: normal;
  background-color: transparent;
  border: 0;
}
</style>
