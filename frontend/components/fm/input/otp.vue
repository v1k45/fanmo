<template>
<div class="flex">
  <input
    v-for="(_, idx) in digits" ref="input" :key="idx" v-model="model[idx]"
    class="fm-otp" type="text" inputmode="numeric"
    :class="{ 'fm-otp--filled': !!(model[idx].length), 'fm-otp--block': block }"
    @input.prevent @keyup="handleKeyUp($event, idx)" @paste="handlePaste" @focus="focus(idx)">
</div>
</template>

<script>
export default {
  props: {
    value: { type: String, default: '' },
    digits: { type: Number, default: 6 },
    block: { type: Boolean, default: false }
  },
  data() {
    return {
      model: [],
      didUserPasteWithLastKeyUp: false
    };
  },
  watch: {
    digits: {
      immediate: true,
      handler() {
        this.model = Array(this.digits).fill('');
      }
    }
  },
  methods: {
    focus(idx = 0) {
      if (!this.$refs.input[idx]) return;
      this.$refs.input[idx].focus();
      this.$refs.input[idx].select();
    },
    handleKeyUp(evt, idx) {
      evt.preventDefault();
      if (this.didUserPasteWithLastKeyUp) {
        this.didUserPasteWithLastKeyUp = false;
        return;
      }
      if (['Backspace', 'Delete'].includes(evt.key)) {
        if (this.model[idx]) {
          this.$set(this.model, idx, '');
        } else if (this.$refs.input[idx - 1]) {
          this.focus(idx - 1);
          this.$set(this.model, idx, '');
        }
      } else if (evt.key === 'ArrowLeft') {
        this.focus(idx - 1);
      } else if (evt.key === 'ArrowRight') {
        this.focus(idx + 1);
      } else if (/^[0-9]$/.test(evt.key)) {
        this.$set(this.model, idx, evt.key);
        this.focus(idx + 1);
      } else if (!/^[0-9]$/.test(this.model[idx])) this.$set(this.model, idx, '');
      this.$forceUpdate();
      this.postProcess();
    },
    handlePaste(evt) {
      evt.stopPropagation();
      evt.preventDefault();
      const paste = (evt.clipboardData || window.clipboardData).getData('text');
      if (!paste.length || !/^[0-9]+$/.test(paste)) return;
      const arr = paste.split('').slice(0, this.digits);
      arr.forEach((char, idx) => {
        this.$set(this.model, idx, char);
      });
      this.didUserPasteWithLastKeyUp = true;
      this.postProcess();
      this.focus(arr.length - 1);
    },
    postProcess() {
      const out = this.model.join('');
      this.$emit('input', out);
      if (out.length === this.digits) this.$emit('filled', out);
    }
  }
};
</script>

<style lang="scss">
.fm-otp {
  @apply inline-block text-2xl w-12 text-center rounded-lg border-gray-300 border bg-white py-2 select-all;
  @apply focus:border-fm-primary;

  &[disabled] {
    @apply cursor-not-allowed bg-gray-50 text-gray-400;
  }

  &~.fm-otp {
    @apply ml-3;
  }
}

.fm-otp--filled {
  @apply border-fm-primary;
}

.fm-otp--block {
  @apply flex-grow;
}
</style>
