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
      v-if="currentPreset.hardBreak" type="button" title="Newline (Shift + Enter)"
      @click="editor.chain().focus().setHardBreak().run()">
      <icon-corner-down-left></icon-corner-down-left>
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
      v-if="currentPreset.link" type="button" title="Link (Coming soon)"
      disabled>
      <icon-link></icon-link>
    </button>
    <button
      v-if="currentPreset.horizontalRule" type="button" title="Divider"
      @click="editor.chain().focus().setHorizontalRule().run()">
      <icon-separator-horizontal></icon-separator-horizontal>
    </button>

  </div>

  <fm-markdown-styled>
    <editor-content class="fm-editor__editor" :style="{ minHeight, maxHeight }" :editor="editor"></editor-content>
  </fm-markdown-styled>
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
  strike: false
});

const preset = (() => {
  const basic = () => ({
    ...options(),
    bold: true,
    italic: true,
    strike: true
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
    link: true // TODO: implement link. to be handled separately
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
      currentPreset: preset[this.preset]() // could and should throw here if incorrect preset value is passed
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
        StarterKit.configure(this.currentPreset)
        // Link.configure({
        //   openOnClick: false
        // })
      ]
    });

    this.editor.on('update', ({ editor }) => {
      this.$emit('input', editor.getHTML());
    });
  },

  beforeDestroy() {
    this.editor.destroy();
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
