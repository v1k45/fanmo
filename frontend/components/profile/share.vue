<template>
<fm-dialog v-model="isVisible" custom-width dialog-class="max-w-md">
  <template #header>Share</template>

  <div>
    Share this via

    <div class="flex justify-between mt-2 mb-6">
      <a class="unstyled hover:scale-105 transition-transform transform" title="Twitter" target="_blank" :href="link.twitter">
        <img class="w-12 h-12" src="~/assets/socials/twitter.png" alt="Twitter logo">
      </a>
      <a class="unstyled hover:scale-105 transition-transform transform" title="Facebook" target="_blank" :href="link.facebook">
        <img class="w-12 h-12" src="~/assets/socials/facebook.png" alt="Facebook logo">
      </a>
      <a class="unstyled hover:scale-105 transition-transform transform" title="WhatsApp" target="_blank" :href="link.whatsapp">
        <img class="w-12 h-12" src="~/assets/socials/whatsapp.png" alt="WhatsApp logo">
      </a>
      <a class="unstyled hover:scale-105 transition-transform transform" title="Telegram" target="_blank" :href="link.telegram">
        <img class="w-12 h-12" src="~/assets/socials/telegram.png" alt="Telegram logo">
      </a>
      <a class="unstyled hover:scale-105 transition-transform transform" title="Reddit" target="_blank" :href="link.reddit">
        <img class="w-12 h-12" src="~/assets/socials/reddit.png" alt="Reddit logo">
      </a>
      <a class="unstyled hover:scale-105 transition-transform transform" title="Email" target="_blank" :href="link.email">
        <img class="w-12 h-12" src="~/assets/socials/gmail.png" alt="Email logo">
      </a>
    </div>

    or copy link

    <div class="flex mt-2 mb-6">
      <fm-input readonly :value="url" class="flex-grow mr-3"></fm-input>
      <fm-button type="primary" class="w-28" :disabled="isCopied" @click="copy">{{ isCopied ? 'Copied' : 'Copy' }}</fm-button>
    </div>

  </div>

</fm-dialog>
</template>

<script>
import { getSocialLink, copy, delay } from '~/utils';

export default {
  props: {
    value: { type: Boolean, default: true },
    relativeUrl: { type: String, default: '' },
    text: { type: String, default: '' }
  },
  data() {
    return {
      isCopied: false
    };
  },
  computed: {
    isVisible: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('input', val);
      }
    },
    url() {
      if (!this.relativeUrl) return '';
      return `${location.origin}${this.relativeUrl.startsWith('/') ? '' : '/'}${this.relativeUrl}`;
    },
    link() {
      const { url, text } = this;
      if (!url || !text) return {
        email: '',
        facebook: '',
        reddit: '',
        telegram: '',
        twitter: '',
        whatsapp: ''
      };
      return {
        email: getSocialLink('email', { url, text }),
        facebook: getSocialLink('facebook', { url, text }),
        reddit: getSocialLink('reddit', { url, text }),
        telegram: getSocialLink('telegram', { url, text }),
        twitter: getSocialLink('twitter', { url, text }),
        whatsapp: getSocialLink('whatsapp', { url, text })
      };
    }
  },
  methods: {
    async copy() {
      try {
        await copy(this.url);
        this.isCopied = true;
        await delay(2000);
        this.isCopied = false;
      } catch (err) {
        this.$toast.error('Copy failed. Please copy manually.');
      }
    }
  }
};
</script>
<style>
</style>
