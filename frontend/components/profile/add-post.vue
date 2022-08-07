<template>
<fm-dialog v-model="isVisible" fullscreen no-padding>
  <template #header>
    <div class="relative">
      <div class="container">Create post</div>
      <logo class="h-5 absolute right-10 top-1"></logo>
    </div>
  </template>

  <div class="container py-6">
    <div class="row">
      <div class="col-12 lg:col-6">
        <fm-form id="createPostForm" :errors="errors" @submit.prevent="handleSubmit">
          <fm-tabs v-model="contentType" stretched>
            <!-- text only post start -->
            <fm-tabs-pane id="text" label="Text" lazy>
              <template v-if="contentType === 'text'">
                <fm-input v-model="form.title" uid="title" type="text" placeholder="Title" input-class="font-bold !text-lg" required></fm-input>
                <fm-input-rich v-model="form.content.text" uid="content.text" preset="advanced" :props="{ minHeight: '200px' }"></fm-input-rich>
              </template>
            </fm-tabs-pane>
            <!-- text only post end -->

            <!-- text+image(s) post start -->
            <fm-tabs-pane id="images" label="Images" lazy>
              <template v-if="contentType === 'images'">
                <fm-input v-model="form.title" uid="title" type="text" placeholder="Title" input-class="font-bold !text-lg" required></fm-input>
                <fm-input v-model="form.content.files" uid="content.files" type="file" label="Images" multiple accept="image/*" required></fm-input>
                <fm-input v-model="form.content.text" uid="content.text" label="Description (optional)" type="textarea"></fm-input>
              </template>
            </fm-tabs-pane>
            <!-- text+image(s) post end -->

            <!-- text+link post start -->
            <fm-tabs-pane id="link" label="Link" lazy>
              <template v-if="contentType === 'link'">
                <fm-input v-model="form.title" uid="title" type="text" placeholder="Title" input-class="font-bold !text-lg" required></fm-input>
                <fm-input v-model="form.content.link" uid="content.link" type="text" label="Link" placeholder="https://example.com/example" required></fm-input>
                <fm-input v-model="form.content.text" uid="content.text" label="Description (optional)" type="textarea"></fm-input>
              </template>
            </fm-tabs-pane>
            <!-- text+link post end -->
          </fm-tabs>

          <!-- visibility start -->
          <fm-input v-model="form.visibility" uid="visibility" type="select" label="Who can see this post?" class="mt-6">
            <option value="public">Public &mdash; Visible to everyone</option>
            <option value="all_members">All members &mdash; Visible to members of all levels</option>
            <option v-if="$auth.user.tiers.length" value="allowed_tiers">Selected members &mdash; Visible to members of selected levels</option>
          </fm-input>

          <div v-if="form.visibility == 'allowed_tiers'" class="mt-4">
            <label class="mb-3 block">Select levels</label>
            <fm-input
              v-for="tier in $auth.user.tiers" :key="tier.id" v-model="form.allowed_tiers_ids"
              name="selected-tiers" type="checkbox" :native-value="tier.id" class="!mt-1">
              {{ tier.name }}
            </fm-input>
          </div>
          <!-- visibility end -->

        </fm-form>
      </div>
      <div class="hidden lg:block col-6">
        <div class="bg-gray-50 min-h-full rounded-lg px-6 py-4">
          <!-- TODO: once breakpoint service is available, add a preview tab for phones -->
          <div class="text-lg font-bold mb-4">Preview</div>
          <!-- preview card start -->
          <fm-card>
            <div class="flex items-center">
              <fm-avatar
                :src="$auth.user.avatar && $auth.user.avatar.small"
                :name="$auth.user.display_name"
                size="w-10 h-10 flex-shrink-0">
              </fm-avatar>
              <div class="ml-3 mr-auto min-w-0">
                <div class="font-bold truncate" :title="$auth.user.name || $auth.user.username">
                  {{ $auth.user.name || $auth.user.username }}
                </div>
                <div class="flex">
                  <div class="text-xs text-gray-500">{{ sampleCreatedAt }}</div>
                </div>
              </div>
            </div>

            <div class="text-xl text-black font-bold mt-4">
              <template v-if="form.title">{{ form.title }}</template>
            </div>

            <fm-read-more-height v-if="form.content.text" max-height="200" class="mt-3">
              <fm-markdown-styled v-html="form.content.text"></fm-markdown-styled>
            </fm-read-more-height>

            <fm-carousel v-if="imagePreviews.length" :images="imagePreviews" class="mt-4">
            </fm-carousel>

            <template v-if="contentType === 'link' && form.content.link">
              <fm-markdown-styled class="mt-4">
                <a :href="form.content.link" target="_blank" class="mt-4">{{ form.content.link }}</a>
              </fm-markdown-styled>
              <div
                v-if="(linkPreview.link && linkPreview.link.toString()) !== form.content.link"
                class="p-16 rounded-lg mt-4 bg-gray-100 text-center" @click="getPreview">
                <fm-button type="info" :loading="loading"><icon-refresh-cw class="h-em w-em"></icon-refresh-cw> Load preview</fm-button>
              </div>
              <div v-else-if="linkPreview.link_embed" class="mt-4 aspect-w-16 aspect-h-9" v-html="linkPreview.link_embed.html">
              </div>
              <a
                v-else-if="linkPreview.link_og && linkPreviewComputed"
                class="unstyled block border overflow-hidden rounded-lg bg-gray-50 mt-3"
                :href="linkPreviewComputed.link" target="_blank" rel="noopener noreferrer nofollow">
                <div v-if="linkPreviewComputed.image" class="overflow-hidden flex-none">
                  <img :src="linkPreviewComputed.image" class="w-full max-h-48 object-cover" alt="">
                </div>
                <div class="p-4 pt-3 flex-grow overflow-hidden">
                  <div class="block font-bold max-w-full">{{ linkPreviewComputed.title }}</div>
                  <div v-if="linkPreviewComputed.description" class="mt-1 text-sm">{{ linkPreviewComputed.description }}</div>
                  <div class="text-gray-500 text-sm mt-1">{{ linkPreviewComputed.hostname }}</div>
                </div>
              </a>
            </template>


            <hr class="mt-4">
            <div class="mt-4 flex items-center">
              <button type="link" class="inline-flex items-center mr-6">
                <icon-heart class="inline mr-2 h-em w-em"></icon-heart>
                Like
              </button>
              <button type="link" class="inline-flex items-center mr-auto">
                <icon-message-square class="inline mr-2 h-em w-em"></icon-message-square>
                Comment
              </button>
              <button type="link" class="inline-flex items-center">
                <icon-share class="inline mr-2 h-em w-em"></icon-share>
                Share
              </button>
            </div>
          </fm-card>
          <!-- preview card end -->
        </div>
      </div>
    </div>
  </div>

  <template #footer>
    <div class="text-right">
      <fm-button :disabled="loading" @click="isVisible = false;">Close</fm-button>
      <fm-button native-type="submit" form="createPostForm" type="primary" :loading="loading">Create post</fm-button>
    </div>
  </template>
</fm-dialog>
</template>

<script>
import dayjs from 'dayjs';
import get from 'lodash/get';
import cloneDeep from 'lodash/cloneDeep';
import { mapActions } from 'vuex';
import FmInputRich from '~/components/fm/input/rich.vue';

const contentPreset = () => ({
  text: {
    type: 'text',
    text: ''
  },
  images: {
    type: 'images',
    text: '',
    files: []
  },
  link: {
    type: 'link',
    text: '',
    link: ''
  }
});

export default {
  components: {
    FmInputRich
  },
  props: {
    value: { type: Boolean, default: false }
  },
  data() {
    const contents = contentPreset();
    return {
      sampleCreatedAt: dayjs().format('D MMM, YYYY hh:mma'),
      contents,
      contentType: 'text',
      form: {
        title: '',
        content: contents.text,
        visibility: 'public',
        allowed_tiers_ids: []
      },
      errors: {},
      linkPreview: {
        link: null,
        link_og: null,
        link_embed: null
      },
      loading: false
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
    imagePreviews() {
      if (!this.form.content.files || !this.form.content.files.length) return [];
      return this.form.content.files.map(file => URL.createObjectURL(file));
    },
    linkPreviewComputed() {
      if (this.contentType !== 'link' || !this.linkPreview.link || !this.form.content.link) return null;
      // eslint-disable-next-line camelcase
      const { link, link_og, link_embed } = this.linkPreview;
      const title = get(link_embed, 'title') || get(link_og, 'og.title') || get(link_og, 'meta.twitter:title') || get(link_og, 'page.title');
      const description = get(link_og, 'og.description') || get(link_og, 'meta.twitter:description') || get(link_og, 'meta.description') || '';
      const image = get(link_og, 'og.image') || get(link_og, 'meta.og:image') || '';
      return {
        link: link.toString(),
        hostname: link.hostname,
        title,
        description,
        image
      };
    }
  },
  watch: {
    isVisible(isVisible) {
      if (!isVisible) this.reset();
      // TODO: you will lose your progress
    },
    contentType(type) {
      if (type === 'text') this.form.content = this.contents.text;
      if (type === 'images') this.form.content = this.contents.images;
      if (type === 'link') this.form.content = this.contents.link;
    }
  },
  methods: {
    ...mapActions('profile', ['createPost', 'getLinkPreview']),
    reset() {
      const contents = contentPreset();
      Object.assign(this, {
        sampleCreatedAt: dayjs().format('D MMM, YYYY hh:mma'),
        contents,
        contentType: 'text',
        form: {
          title: '',
          content: contents.text,
          visibility: 'public',
          allowed_tiers_ids: []
        },
        errors: {},
        linkPreview: {
          link: null,
          link_og: null,
          link_embed: null
        },
        loading: false
      });
    },
    async getBase64(file) {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      const fileReaderResult = await new Promise(resolve => {
        reader.onload = loadEvent => resolve(loadEvent);
      });
      return fileReaderResult.target.result;
    },
    async handleSubmit() {
      this.loading = true;
      const payload = cloneDeep(this.form);
      if (this.contentType === 'images') {
        const base64s = await Promise.all(payload.content.files.map(file => this.getBase64(file)));
        payload.content.files = base64s.map(b64 => ({ type: 'image', image_base64: b64 }));
      }
      if (payload.content.text && /^(<p>\s*<\/p>)+$/.test(payload.content.text.trim())) payload.content.text = '';
      const { success, data } = await this.createPost(payload);
      if (!success) {
        this.errors = data;
        this.loading = false;
        return;
      }
      this.$toast.success('Your post was published successfully. Your followers will be notified shortly.');
      await this.$router.push({ name: 'p-slug-id', params: { slug: data.slug, id: data.id, share: '1' } });
      this.loading = false;
      this.isVisible = false;
    },
    async getPreview() {
      this.loading = true;
      const { success, data } = await this.getLinkPreview(this.form.content.link);
      this.loading = false;
      if (!success) {
        if (data.link) data.content = { link: data.link };
        this.errors = data;
        return;
      }
      this.linkPreview = {
        ...data,
        link: new URL(data.link)
      };
      if (!this.form.title) {
        this.form.title = this.linkPreviewComputed.title;
      }
      if (this.errors.content && this.errors.content.link) this.errors.content.link = null;
    }
  }
};
</script>
<style>
/* TODO: use predetermined dimensions for popular sites */
/* .embed-content > iframe {
  width: 100% !important;
} */
/* https://open.spotify.com/track/0uk9sQ7MjK0CdAUinD4xBV?si=a3a78b1b453942a5 */
</style>
