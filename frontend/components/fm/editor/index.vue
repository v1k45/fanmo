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
      v-if="currentPreset.bold" type="button"
      :class="{ 'is-active': editor.isActive('bold') }" @click="editor.chain().focus().toggleBold().run()">
      <icon-bold></icon-bold>
    </button>
    <button
      v-if="currentPreset.italic" type="button"
      :class="{ 'is-active': editor.isActive('italic') }" @click="editor.chain().focus().toggleItalic().run()">
      <icon-italic></icon-italic>
    </button>
    <button
      v-if="currentPreset.strike" type="button"
      :class="{ 'is-active': editor.isActive('strike') }" @click="editor.chain().focus().toggleStrike().run()">
      <icon-strikethrough></icon-strikethrough>
    </button>


    <hr v-if="(currentPreset.heading || currentPreset.bold || currentPreset.italic || currentPreset.strike) && (currentPreset.bulletList || currentPreset.orderedList)">

    <button
      v-if="currentPreset.bulletList" type="button"
      :class="{ 'is-active': editor.isActive('bulletList') }" @click="editor.chain().focus().toggleBulletList().run()">
      <icon-list></icon-list>
    </button>
    <button
      v-if="currentPreset.orderedList" type="button"
      :class="{ 'is-active': editor.isActive('orderedList') }" @click="editor.chain().focus().toggleOrderedList().run()">
      <icon-list-ordered></icon-list-ordered>
    </button>

    <hr v-if="(currentPreset.heading || currentPreset.bold || currentPreset.italic || currentPreset.strike || currentPreset.bulletList || currentPreset.orderedList) && (currentPreset.blockquote || currentPreset.link)">

    <button
      v-if="currentPreset.blockquote" type="button"
      :class="{ 'is-active': editor.isActive('blockquote') }" @click="editor.chain().focus().toggleBlockquote().run()">
      <icon-quote></icon-quote>
    </button>
    <button
      v-if="currentPreset.link" type="button"
      disabled>
      <icon-link></icon-link>
    </button>
    <button
      v-if="currentPreset.horizontalRule" type="button"
      @click="editor.chain().focus().setHorizontalRule().run()">
      <icon-separator-horizontal></icon-separator-horizontal>
    </button>

  </div>

  <editor-content class="fm-editor__editor" :style="{ maxHeight }" :editor="editor"></editor-content>
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

  blockquote: false,
  bold: false,
  bulletList: false,
  code: false,
  codeBlock: false,
  dropcursor: false,
  gapcursor: false,
  hardBreak: false, // TODO: implement single enter - this, double enter - paragraph
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
.fm-editor__toolbar {
  @apply flex border border-gray-300 rounded-lg rounded-b-none;
  button {
    @apply rounded-lg my-1 mx-3 p-2;
    & + button {
      @apply ml-0;
    }
    &:hover {
      @apply text-gray-800;
    }
    &.is-active {
      @apply bg-gray-500 text-white;
    }
  }
  hr {
    @apply block h-auto border border-dashed;
  }
  svg {
    @apply h-5 w-5;
  }
  .is-active, > * {
    @apply stroke-[3px];
  }
}
.fm-editor__editor {
  @apply border border-gray-300 border-t-0 rounded-lg rounded-t-none py-4 px-4 overflow-auto;
  > .ProseMirror {
    @apply min-h-[100px] outline-none;

    > * + * {
      margin-top: 0.75em;
    }

    ul,
    ol {
      @apply px-4;
    }
    ul {
      @apply list-disc;
    }
    ol {
      @apply list-decimal;
    }

    h3 {
      @apply text-2xl;
    }

    blockquote {
      @apply pl-4 border-l-2 border-gray-300 text-gray-500 ;
    }

    hr {
      @apply border-0 border-gray-300 border-t my-4;
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
</style>
