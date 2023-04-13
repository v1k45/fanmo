<template>
<div v-if="editor" class="fm-editor">

  <div class="fm-editor__toolbar">

    <button
      v-if="currentPreset.heading"
      type="button" :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
      @click="editor.chain().focus().toggleHeading({ level: 3 }).run()">
      <icon-type></icon-type>
    </button>


    <hr v-if="currentPreset.heading && (currentPreset.bold || currentPreset.italic || currentPreset.strike)">

    <button
      v-if="currentPreset.bold" type="button" title="Bold"
      :class="{ 'is-active': editor.isActive('bold') }" @click="editor.chain().focus().toggleBold().run()">
      <icon-bold></icon-bold>
    </button>
    <button
      v-if="currentPreset.italic" type="button" title="Italic"
      :class="{ 'is-active': editor.isActive('italic') }" @click="editor.chain().focus().toggleItalic().run()">
      <icon-italic></icon-italic>
    </button>
    <button
      v-if="currentPreset.strike" type="button" title="Strikethrough"
      :class="{ 'is-active': editor.isActive('strike') }" @click="editor.chain().focus().toggleStrike().run()">
      <icon-strikethrough></icon-strikethrough>
    </button>
    <button
      type="button" title="Link"
      :class="{ 'is-active': editor.isActive('link') }" :disabled="editor.view.state.selection.empty && !editor.isActive('link')"
      @click="setLink">
      <icon-link></icon-link>
    </button>
    <button
      v-if="currentPreset.image" type="button" title="Image"
      :class="{ 'is-active': editor.isActive('image') }"
      @click="setImage">
      <icon-image></icon-image>
    </button>
    <button
      v-if="currentPreset.hardBreak" type="button" title="Newline (Shift + Enter)"
      @click="editor.chain().focus().setHardBreak().run()">
      <icon-corner-down-left></icon-corner-down-left>
    </button>

    <hr v-if="currentPreset.textAlign">
    <button
      v-if="currentPreset.textAlign" type="button" title="Align Left"
      :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }" @click="toggleAlign('left')">
      <icon-align-left></icon-align-left>
    </button>
    <button
      v-if="currentPreset.textAlign" type="button" title="Align Center"
      :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" @click="toggleAlign('center')">
      <icon-align-center></icon-align-center>
    </button>
    <button
      v-if="currentPreset.textAlign" type="button" title="Align Right"
      :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" @click="toggleAlign('right')">
      <icon-align-right></icon-align-right>
    </button>

    <hr v-if="(currentPreset.heading || currentPreset.bold || currentPreset.italic || currentPreset.strike || currentPreset.hardBreak) && (currentPreset.bulletList || currentPreset.orderedList)">

    <button
      v-if="currentPreset.bulletList" type="button" title="Bullet list"
      :class="{ 'is-active': editor.isActive('bulletList') }" @click="editor.chain().focus().toggleBulletList().run()">
      <icon-list></icon-list>
    </button>
    <button
      v-if="currentPreset.orderedList" type="button" title="Ordered list"
      :class="{ 'is-active': editor.isActive('orderedList') }" @click="editor.chain().focus().toggleOrderedList().run()">
      <icon-list-ordered></icon-list-ordered>
    </button>

    <hr v-if="(currentPreset.heading || currentPreset.bold || currentPreset.italic || currentPreset.strike || currentPreset.bulletList || currentPreset.orderedList) && (currentPreset.blockquote || currentPreset.link)">

    <button
      v-if="currentPreset.blockquote" type="button" title="Quote"
      :class="{ 'is-active': editor.isActive('blockquote') }" @click="editor.chain().focus().toggleBlockquote().run()">
      <icon-quote></icon-quote>
    </button>
    <button
      v-if="currentPreset.horizontalRule" type="button" title="Divider"
      @click="editor.chain().focus().setHorizontalRule().run()">
      <icon-separator-horizontal></icon-separator-horizontal>
    </button>

  </div>

  <fm-markdown-styled>
    <editor-content class="fm-editor__editor" :class="{ 'resize-y': preset === 'advanced' }" :style="{ minHeight, maxHeight }" :editor="editor"></editor-content>
  </fm-markdown-styled>

  <fm-dialog v-model="imageUploader.isVisible">
    <template #header><div class="text-base">Insert an image</div></template>
    <div class="text-sm">
      <fm-form :errors="imageUploader.errors" @submit.prevent="">
        <fm-input v-model="imageUploader.form.image_base64" uid="image_base64" type="file" accept="image/*"></fm-input>
      </fm-form>
    </div>
    <template #footer>
      <div class="text-right">
        <fm-button :disabled="imageUploader.loading" @click="imageUploader.isVisible = false;">Close</fm-button>
        <fm-button type="primary" :loading="imageUploader.loading" @click="uploadImage">Upload</fm-button>
      </div>
    </template>
  </fm-dialog>

</div>
<div v-else>
  Loading...
</div>
</template>

<script>
import {
  Italic as IconItalic,
  Bold as IconBold,
  Strikethrough as IconStrikethrough,
  List as IconList,
  ListOrdered as IconListOrdered,
  Quote as IconQuote,
  Type as IconType,
  SeparatorHorizontal as IconSeparatorHorizontal,
  Link as IconLink
} from 'lucide-vue';
import { Editor, EditorContent } from '@tiptap/vue-2';
import StarterKit from '@tiptap/starter-kit';
import LinkExtension from '@tiptap/extension-link';
import TextAlignExtension from '@tiptap/extension-text-align';
import ImageExtension from '@tiptap/extension-image';
import cloneDeep from 'lodash/cloneDeep';
import { getBase64FromFile, handleGenericError } from '~/utils';

const options = () => ({
  document: true,
  history: true,
  paragraph: true,
  text: true,
  hardBreak: true, // TODO: implement single enter - this, double enter - paragraph (very hard)

  blockquote: false,
  bold: false,
  bulletList: false,
  code: false,
  codeBlock: false,
  dropcursor: false,
  gapcursor: false,
  heading: false,
  horizontalRule: false,
  italic: false,
  listItem: false,
  orderedList: false,
  textAlign: false,
  strike: false
});

const preset = (() => {
  const basic = () => ({
    ...options(),
    bold: true,
    italic: true,
    strike: true,
    link: true
  });
  const intermediate = () => ({
    ...basic(),
    bulletList: true,
    orderedList: true,
    listItem: true
  });
  const advanced = () => ({
    ...intermediate(),
    heading: {
      levels: [3]
    },
    blockquote: true,
    horizontalRule: true,
    image: true,
    textAlign: true
  });
  return {
    basic,
    intermediate,
    advanced
  };
})();

export default {
  components: {
    IconItalic,
    IconBold,
    IconStrikethrough,
    IconList,
    IconListOrdered,
    IconQuote,
    IconSeparatorHorizontal,
    IconLink,
    IconType,
    EditorContent
  },

  props: {
    value: { type: String, default: '' },
    preset: { type: String, default: 'basic', validator: val => Object.keys(preset).includes(val) },
    minHeight: { type: String, default: '100px' },
    maxHeight: { type: String, default: '200px' }
  },

  data() {
    return {
      editor: null,
      currentPreset: preset[this.preset](), // could and should throw here if incorrect preset value is passed
      imageUploader: {
        isVisible: false,
        loading: false,
        form: { image_base64: '' },
        errors: {}
      }
    };
  },

  watch: {
    value(value) {
      if (!this.editor) return false;
      if (this.editor.getHTML() === value) return;
      this.editor.commands.setContent(value);
    }
  },

  mounted() {
    this.editor = new Editor({
      content: this.value,
      extensions: [
        StarterKit.configure(this.currentPreset),
        ...(this.currentPreset.link ? [LinkExtension.configure({ openOnClick: false })] : []),
        ...(this.currentPreset.image ? [ImageExtension] : []),
        ...(this.currentPreset.textAlign ? [TextAlignExtension.configure({ types: ['heading', 'paragraph'] })] : [])
      ]
    });

    this.editor.on('update', ({ editor }) => {
      this.$emit('input', editor.getHTML());
    });
  },

  beforeDestroy() {
    this.editor.destroy();
  },

  methods: {
    setLink() {
      const previousUrl = this.editor.getAttributes('link').href;
      let url = window.prompt('URL', previousUrl);

      // cancelled
      if (url === null) return;

      // empty
      if (url === '') {
        this.editor.chain().focus().extendMarkRange('link').unsetLink().run();
        return;
      }

      // prevent unexpected relative URLs
      if (!url.startsWith('http') || !url.startsWith('mailto')) {
        url = 'http://' + url;
      }

      // update link
      this.editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
    },
    setImage() {
      this.imageUploader.isVisible = true;
    },
    async uploadImage() {
      this.loading = true;
      try {
        const imageBase64 = await getBase64FromFile(cloneDeep(this.imageUploader.form).image_base64);
        const postImage = await this.$axios.$post('/api/images/', { image_base64: imageBase64 });
        this.editor.chain().focus().insertContent([
          {
            type: 'image',
            attrs: {
              src: postImage.image.medium
            }
          },
          {
            type: 'hardBreak'
          }
        ]).run();
        this.imageUploader.isVisible = false;
        this.imageUploader.form.image_base64 = '';
      } catch (err) {
        handleGenericError(err);
        this.imageUploader.errors = err.response.data;
      }
      this.loading = false;
    },
    toggleAlign(direction) {
      if (this.editor.isActive({ textAlign: direction })) {
        this.editor.chain().focus().unsetTextAlign().run();
      } else {
        this.editor.chain().focus().setTextAlign(direction).run();
      }
    }
  }
};
</script>
italic, bold, strikethrough, list, paragraph, h1-h6, blockquote, hr

<style lang="scss">
.fm-editor {
  @apply flex flex-col;
}

.fm-editor__toolbar {
  @apply flex border border-gray-300 rounded-lg rounded-b-none overflow-auto;
  button {
    @apply rounded-lg my-1 mx-3 p-2;
    & + button {
      @apply ml-0;
    }
    &:hover {
      @apply text-gray-800;
    }
    &:disabled {
      @apply text-gray-400;
    }
    &.is-active {
      @apply bg-gray-100 text-black;
    }
  }
  hr {
    @apply block h-auto border;
  }
  svg {
    @apply h-5 w-5;
  }
  .is-active > * {
    @apply stroke-[3px];
  }
}
.fm-editor__editor {
  @apply border border-gray-300 border-t-0 rounded-lg rounded-t-none py-4 px-4 overflow-auto flex-grow flex;
  > .ProseMirror {
    @apply min-h-[100px] h-max outline-none flex-grow;
    img.ProseMirror-selectednode {
      @apply ring ring-offset-0 ring-gray-500
    }
  }
}

.fm-editor:focus-within {
  .fm-editor__toolbar,
  .fm-editor__editor {
    @apply transition-colors ring-1 ring-fm-primary border-fm-primary;
  }
  .fm-editor__toolbar hr {
    @apply border-fm-primary;
  }
}
.fm-editor:focus-within {
  .fm-editor__toolbar,
  .fm-editor__editor {
    @apply transition-colors ring-1 ring-gray-600 border-gray-600;
  }
  .fm-editor__toolbar hr {
    @apply border-gray-600;
  }
}
</style>
