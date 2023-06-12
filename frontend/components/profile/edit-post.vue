<template>
<fm-dialog v-model="isVisible" fullscreen no-padding require-explicit-close>
  <template #header>
    <div class="relative">
      <div class="container">Edit post</div>
      <logo class="h-5 absolute right-10 top-1"></logo>
    </div>
  </template>

  <div class="container py-6">
    <div class="row">
      <div class="col-12 max-w-6xl mx-auto">
        <fm-form id="updatePostForm" :errors="errors" @submit.prevent="handleSubmit">

          <template v-if="contentType === 'text'">
            <fm-input v-model="form.title" uid="title" type="text" placeholder="Title" input-class="font-bold !text-lg" required></fm-input>
            <fm-input-rich v-model="form.content.text" uid="content.text" preset="advanced" :props="{ minHeight: '400px', maxHeight: '70vh' }"></fm-input-rich>
          </template>
          <template v-else-if="contentType === 'images'">
            <fm-input v-model="form.title" uid="title" type="text" placeholder="Title" input-class="font-bold !text-lg" required></fm-input>
            <div v-if="false" class="text-sm">

            </div>
            <fm-input v-if="false" v-model="form.content.files" uid="content.files" type="file" label="Images" multiple accept="image/*" required></fm-input>
            <fm-input v-model="form.content.text" uid="content.text" label="Description (optional)" type="textarea"></fm-input>
            <fm-alert class="text-sm my-4" title="Editing images is currently not supported" message="Adding or removing images from an already published image post is currently not possible."></fm-alert>
          </template>
          <template v-else-if="contentType === 'link'">
            <fm-input v-model="form.title" uid="title" type="text" placeholder="Title" input-class="font-bold !text-lg" required></fm-input>
            <fm-input v-model="form.content.link" uid="content.link" type="text" label="Link" placeholder="https://example.com/example" required></fm-input>
            <fm-input v-model="form.content.text" uid="content.text" label="Description (optional)" type="textarea"></fm-input>
          </template>

          <hr class="my-4">

          <!-- visibility start -->
          <fm-collapse
            v-model="isExpanded.visibility"
            icon="eye"
            title="Visibility"
            description="Choose who can see this post"
            class="p-3"
            :class="{'bg-gray-50 rounded-sm': isExpanded.visibility}">
            <fm-input v-model="form.visibility" uid="visibility" type="select" label="Who can see this post?" class="mt-6">
              <option value="public">Public &mdash; Visible to everyone</option>
              <option value="all_members">All members &mdash; Visible to members of all tiers</option>
              <option v-if="$auth.user.tiers.length" value="allowed_tiers">Selected members &mdash; Visible to members of selected tiers</option>
            </fm-input>

            <div v-if="form.visibility == 'allowed_tiers'" class="mt-4">
              <label class="mb-3 block">Select tiers</label>
              <fm-input
                v-for="tier in $auth.user.tiers" :key="tier.id" v-model="form.allowed_tiers_ids"
                name="selected-tiers" type="checkbox" :native-value="tier.id" class="!mt-1">
                {{ tier.name }}
              </fm-input>
            </div>
          </fm-collapse>
          <!-- visibility end -->

          <hr class="my-4">

          <!-- monetization start -->
          <fm-collapse
            v-model="isExpanded.monetization"
            icon="indian-rupee"
            title="Monetization"
            description="Allow non-members to unlock this post by sending a tip"
            class="p-3"
            :class="{'bg-gray-50 rounded-sm': isExpanded.monetization}">

            <div class="xmt-2" foo="p-2 border border-gray-300 rounded">
              <fm-input v-model="form.is_purchaseable" uid="is_purchaseable" type="checkbox">Allow non-members to purchase this post</fm-input>
              <div class="text-gray-500 text-sm">
                Users who are not your members will be able to unlock this post by sending you a tip of their choice.
              </div>
              <fm-input
                v-if="form.is_purchaseable"
                v-model.number="form.minimum_amount" type="number" uid="minimum_amount" label="Minimum Amount" class="mt-2"
                :min="$auth.user.preferences.minimum_amount" max="10000" placeholder="Enter an amount">
                <template #after-label>
                  <div class="flex space-x-1 overflow-auto pb-1 mb-1">
                    <button
                      v-for="amount in presetAmounts" :key="amount" type="button"
                      class="py-1 px-2 text-sm rounded border border-fm-primary-400 hover:border-fm-primary-500 hover:bg-fm-primary-500 hover:text-white"
                      :class="{'border-fm-primary-500 bg-fm-primary-500 text-white': parseFloat(amount) === parseFloat(form.minimum_amount), 'text-fm-primary-400': parseFloat(amount) !== parseFloat(form.minimum_amount)}"
                      @click="form.minimum_amount = amount;">
                      {{ $currency(amount) }}
                    </button>
                  </div>
                </template>
                <template #prepend>₹</template>
              </fm-input>
            </div>
          </fm-collapse>
          <!-- monetization end -->

          <hr class="my-4">
          <!-- preview start -->
          <fm-collapse
            v-model="isExpanded.preview"
            icon="view"
            title="Preview"
            description="See how this post will look like when it is published"
            class="p-3"
            :class="{'bg-gray-50 rounded-sm': isExpanded.preview}">
            <div class="bg-gray-50 min-h-full rounded-lg md:px-6 md:py-4">
              <!-- TODO: once breakpoint service is available, add a preview tab for phones -->
              <!-- preview card start -->
              <div class="bg-white rounded-xl border pt-4 pb-1">
                <div class="post-body">

                  <div v-if="form.title" class="flex items-center">
                    <div class="flex flex-wrap flex-grow mr-auto">
                      <div class="w-full basis-auto unstyled" title="Open post">
                        <div class="text-lg md:text-xl text-black font-bold w-full">{{ form.title }}</div>
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-wrap items-center mt-1 text-xs">

                    <!-- avatar and name start -->
                    <div class="unstyled flex items-center mr-auto mt-1 overflow-hidden md:max-w-[47.5%]">
                      <!-- avatar start -->
                      <fm-avatar
                        :src="$auth.user.avatar && $auth.user.avatar.small"
                        :name="$auth.user.display_name"
                        size="w-5 h-5 flex-shrink-0">
                      </fm-avatar>
                      <!-- avatar end -->

                      <!-- name start -->
                      <div class="ml-2 min-w-0 text-sm truncate">
                        <div class="truncate" :title="$auth.user.display_name">{{ $auth.user.display_name }}</div>
                      </div>
                      <!-- name end -->
                    </div>
                    <!-- avatar and name end -->

                    <div class="ml-7 md:ml-0 flex items-center text-gray-500 overflow-hidden mt-1 md:max-w-[47.5%]">
                      <div class="text-gray-500 flex-shrink-0">{{ sampleCreatedAt }}</div>
                      <span class="mx-2">&bull;</span>
                      <div
                        v-tooltip="{ content: visibilityPreviewNormalized, disabled: form.visibility === 'public' }"
                        tabindex="0" class="truncate">
                        <icon-lock v-if="form.visibility !== 'public'" class="h-em w-em -mt-1"></icon-lock>
                        <icon-globe v-if="form.visibility === 'public'" class="h-em w-em -mt-1"></icon-globe>
                        {{ visibilityPreviewNormalized }}
                      </div>
                    </div>
                  </div>
                </div>

                <template v-if="form.content">
                  <div v-if="form.content.text" class="post-body">
                    <fm-read-more-height :max-height="$route.name == 'p-slug-id' ? null : '300'" class="mt-4">
                      <fm-markdown-styled>
                        <div class="whitespace-pre-line" v-html="form.content.text"></div>
                      </fm-markdown-styled>
                    </fm-read-more-height>
                  </div>

                  <fm-carousel v-if="imagePreviews.length" :images="imagePreviews" class="mt-4"></fm-carousel>

                  <div v-if="contentType === 'link' && form.content.link" class="post-body">

                    <fm-markdown-styled class="mt-4">
                      <a :href="form.content.link" target="_blank" class="mt-4">{{ form.content.link }}</a>
                    </fm-markdown-styled>

                    <div
                      v-if="(linkPreview.link && linkPreview.link.toString()) !== form.content.link"
                      class="p-16 rounded-lg mt-4 bg-gray-100 text-center" @click.prevent="getPreview">
                      <fm-button type="info" :loading="loading" @click.prevent="getPreview"><icon-refresh-cw class="h-em w-em"></icon-refresh-cw> Load preview</fm-button>
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
                  </div>
                </template>

                <hr v-if="!imagePreviews.length && form.content" class="mt-4">
                <div class="mt-4 mb-3 post-body flex items-center">
                  <button type="link" class="inline-flex items-center mr-6" @click.prevent="">
                    <icon-heart class="inline mr-2 h-em w-em"></icon-heart>
                    Like
                  </button>
                  <button type="link" class="inline-flex items-center mr-auto" @click.prevent="">
                    <icon-message-square class="inline mr-2 h-em w-em"></icon-message-square>
                    Comment
                  </button>
                  <button type="link" class="inline-flex items-center" @click.prevent="">
                    <icon-share class="inline mr-2 h-em w-em"></icon-share>
                    Share
                  </button>
                </div>
              </div>
              <!-- preview card end -->
            </div>
          </fm-collapse>

          <!-- preview end -->

          <hr class="my-4">

          <!-- seo settings start -->
          <fm-collapse
            v-model="isExpanded.meta"
            icon="megaphone"
            title="SEO and Social Sharing"
            description="Customize how this post appears on search and social media sites"
            class="p-3"
            :class="{'bg-gray-50 rounded-sm': isExpanded.meta}">
            <fm-input v-model="form.meta.title" label="Title" uid="meta.title" type="text" :placeholder="`${form.title || 'Title'} - ${$auth.user.display_name}`" maxlength="255"></fm-input>
            <fm-input v-model="form.meta.description" label="Description" uid="meta.description" type="textarea" :placeholder="`Support ${$auth.user.display_name} on Fanmo. Become a member, get access to exclusive content, send tips and much more on Fanmo.`" maxlength="500"></fm-input>
            <fm-input v-model="form.meta.keywords" label="Keywords" uid="meta.keywords" type="text" placeholder="comma, seperated, seo, keywords" maxlength="255"></fm-input>
            <fm-input v-model="form.meta.image_base64" uid="meta.image_base64" label="Image" type="file" accept="image/*"></fm-input>
          </fm-collapse>
          <!-- seo settings end -->

        </fm-form>
      </div>
    </div>
  </div>

  <template #footer>
    <div class="text-right">
      <fm-button :disabled="loading" @click="isVisible = false;">Close</fm-button>
      <fm-button native-type="submit" form="updatePostForm" type="primary" :loading="loading">Update post</fm-button>
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
import { getBase64FromFile } from '~/utils';

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
    value: { type: Boolean, default: false },
    post: { type: Object, default: null }
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
        meta: {
          title: '',
          description: '',
          keywords: '',
          image_base64: ''
        },
        is_purchaseable: false,
        minimum_amount: parseFloat(this.$auth.user.preferences.default_donation_amount),
        visibility: 'public',
        allowed_tiers_ids: []
      },
      errors: {},
      linkPreview: {
        link: null,
        link_og: null,
        link_embed: null
      },
      isExpanded: {
        meta: false,
        visibility: true,
        preview: false,
        monetization: false
      },
      showMeta: false,
      showPreview: true,
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
    presetAmounts() {
      return [25, 50, 100, 250, 500, 1000, 2500, 5000].filter(amount => amount >= this.$auth.user.preferences.minimum_amount);
    },
    imagePreviews() {
      if (!this.form.content.files || !this.form.content.files.length) return [];
      return this.form.content.files.map(file => file.id ? file.image.medium : URL.createObjectURL(file));
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
    },
    visibilityPreviewNormalized() {
      const visibilityMap = {
        public: 'Public',
        all_members: 'All members',
        allowed_tiers: this.$auth.user.tiers
          .filter(tier => this.form.allowed_tiers_ids.includes(tier.id))
          .map(tier => tier.name).join(', ')
      };
      return visibilityMap[this.form.visibility];
    }
  },
  watch: {
    isVisible(isVisible) {
      if (!isVisible) this.reset();
      // TODO: you will lose your progress
    }
  },
  created() {
    this.contentType = this.post.content.type;
    this.form.title = this.post.title;
    this.form.content = contentPreset()[this.post.content.type];
    this.form.content.text = this.post.content.text;

    if (this.post.meta) {
      this.form.meta.title = this.post.meta.title;
      this.form.meta.description = this.post.meta.description;
      this.form.meta.keywords = this.post.meta.keywords;
      this.form.meta.image_base64 = this.post.meta.image ? this.post.meta.image.medium : '';
    }

    this.form.is_purchaseable = this.post.is_purchaseable;
    this.form.minimum_amount = parseFloat(this.post.minimum_amount);
    if (this.form.minimum_amount === 0) {
      this.form.minimum_amount = parseFloat(this.$auth.user.preferences.default_donation_amount);
    }

    if (this.post.content.type === 'images') {
      this.form.content.files = this.post.content.files;
    } else if (this.post.content.type === 'link') {
      this.form.content.link = this.post.content.link;
      this.linkPreview.link = new URL(this.post.content.link);
      this.linkPreview.link_embed = this.post.content.link_embed;
      this.linkPreview.link_og = this.post.content.link_og;
    }

    this.form.visibility = this.post.visibility;
    this.form.allowed_tiers_ids = this.post.allowed_tiers.map(t => t.id);
  },
  methods: {
    ...mapActions('profile', ['getLinkPreview']),
    ...mapActions('posts', ['updatePost']),
    reset() {
      const contents = contentPreset();
      Object.assign(this, {
        sampleCreatedAt: dayjs().format('D MMM, YYYY hh:mma'),
        contents,
        contentType: 'text',
        form: {
          title: '',
          content: contents.text,
          meta: {
            title: '',
            description: '',
            keywords: '',
            image_base64: ''
          },
          is_purchaseable: false,
          minimum_amount: parseFloat(this.$auth.user.preferences.default_donation_amount),
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
        // TODO: Handle image uploads
        payload.content.files = payload.content.files.map(b64 => ({ type: 'image', image_base64: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==' }));
      }
      if (payload.content.text && /^(<p>\s*<\/p>)+$/.test(payload.content.text.trim())) payload.content.text = '';
      // adding new
      if (payload.meta.image_base64 && typeof payload.meta.image_base64 !== 'string') payload.meta.image_base64 = await getBase64FromFile(payload.meta.image_base64);
      // deleting existing
      // eslint-disable-next-line brace-style
      else if (this.post.meta && this.post.meta.image && !payload.meta.image_base64) { /* nothing */ }
      // unchanged
      else delete payload.meta.image_base64;

      const { success, data } = await this.updatePost({ postId: this.post.id, payload });
      if (!success) {
        this.errors = data;
        this.loading = false;
        return;
      }
      this.$toast.success('Your post was updated successfully.');
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
