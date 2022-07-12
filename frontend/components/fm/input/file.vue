<template>
<div>
  <div
    class="rounded-lg border border-dashed" tabindex="0"
    :class="{ 'border-fm-primary bg-fm-primary-50': isDraggingOver, 'border-gray-300 bg-gray-100': !isDraggingOver }"
    @dragenter.prevent @dragover.prevent="dragover" @dragleave="dragleave" @drop.prevent="drop" @keyup.enter="$refs.file.click();">
    <label class="relative block cursor-pointer text-center" :class="{ 'p-12': multiple, 'p-6': !multiple }">
      <div>
        <template v-if="multiple">Click here to select files or drag them here.</template>
        <template v-else>Click here to select a file or drag it here.</template>
      </div>
      <input ref="file" type="file" tabindex="-1" :multiple="multiple" v-bind="$attrs" class="w-full h-full top-0 left-0 opacity-0 overflow-hidden cursor-pointer absolute" @change="onChange">
    </label>
  </div>
  <ul v-if="fileList.length" class="flex flex-wrap">
    <li v-for="(file, idx) in fileList" :key="idx" class="relative mt-4 mr-4">
      <img :src="previews[idx]" :alt="file.file.name || ''" class="h-24 rounded-lg border cursor-pointer" @click="showFullSize(file, previews[idx])">
      <div class="mt-1 h-5 relative">
        <div class="absolute text-sm max-w-full truncate text-gray-500" :title="file.file.name || ''">{{ file.file.name || 'uploaded_file' }}</div>
      </div>
      <button
        class="absolute -top-1 -right-1 rounded-full bg-fm-error text-white p-0.5 hover:scale-105 transition-transform"
        type="button" title="Remove file" @click="remove(idx)">
        <icon-x class="!block h-4 w-4"></icon-x>
      </button>
    </li>
  </ul>
  <fm-dialog v-model="fullSize.isVisible" no-padding>
    <template #header>
      <div v-if="fullSize.isVisible" class="truncate">{{ fullSize.file.file.name || 'uploaded_file' }}</div>
    </template>
    <img v-if="fullSize.isVisible" :src="fullSize.preview" :alt="fullSize.file.file.name || 'uploaded_file'" class="w-full">
  </fm-dialog>
</div>
</template>

<script>
export default {
  props: {
    value: { type: [Array, File, String], default: null },
    multiple: { type: Boolean, default: false }
  },
  data() {
    return {
      fullSize: {
        isVisible: false,
        file: null,
        preview: null
      },
      isPreviewing: false,
      isDraggingOver: false,
      fileList: []
    };
  },
  computed: {
    previews() {
      return this.fileList.map(file => file.type === 'file' ? URL.createObjectURL(file.file) : file.file);
    }
  },
  watch: {
    value: {
      immediate: true,
      handler(val) {
        if (this.multiple) {
          // eslint-disable-next-line no-lonely-if
          if (Array.isArray(val)) {
            const isSame = val.every((valFile, idx) => (this.fileList[idx] || {}).file === valFile);
            // assume it's an array of strings (urls)
            if (!isSame) {
              this.fileList = val.map(valFile => ({ type: 'url', file: valFile }));
              this.$refs.file.value = '';
            }
          } else if (val && typeof val === 'string') { // should not be the case except for the first time
            const hasThisFile = this.fileList.find(file => file.file === val);
            if (!hasThisFile) this.fileList = [{ type: 'url', file: val }];
          } else if (!val && typeof val === 'string') {
            this.fileList = [];
          } else if (typeof val === 'object') { // assume it's a File instance
            // assume it's a File instance and do nothing because this should never be the case with `multiple` set
          }
        } else {
          // eslint-disable-next-line no-lonely-if
          if (Array.isArray(val)) throw new Error('Array values are only supported with `multiple` set.');
          else if (val && typeof val === 'string') {
            const hasThisFile = this.fileList.find(file => file.file === val);
            if (!hasThisFile) this.fileList = [{ type: 'url', file: val }];
          } else if (!val && typeof val === 'string') {
            this.fileList = [];
          } else if (typeof val === 'object') {
            // assume it's a File instance and do nothing because it's emitted and set by this component
          }
        }
      }
    }
  },
  methods: {
    onChange() {
      const existingFiles = this.fileList.filter(file => file.type === 'url');
      const inputFiles = [...this.$refs.file.files].map(file => ({ type: 'file', file }));

      if (this.multiple) {
        this.fileList = [...existingFiles, ...inputFiles];
      } else {
        const allFiles = [...inputFiles, ...existingFiles];
        this.fileList = allFiles[0] ? [allFiles[0]] : [];
      }
      this.$emit('input', this.multiple
        ? this.fileList.map(file => file.file)
        : (this.fileList[0] ? this.fileList[0].file : '')
      );
    },
    remove(i) {
      if (this.fileList[i].type === 'url') {
        this.fileList.splice(i, 1);
      } else {
        const allFiles = new DataTransfer();
        this.fileList.forEach((file, idx) => {
          if (i === idx || file.type === 'url') return;
          allFiles.items.add(file.file);
        });
        this.$refs.file.files = allFiles.files;
      }
      this.onChange();
    },
    dragover(event) {
      this.isDraggingOver = true;
    },
    dragleave(event) {
      this.isDraggingOver = false;
    },
    drop(event) {
      this.isDraggingOver = false;
      if (this.multiple) {
        const allFiles = new DataTransfer();
        this.fileList.forEach(file => {
          if (file.type === 'url') return;
          allFiles.items.add(file.file);
        });
        [...event.dataTransfer.files].forEach(file => {
          allFiles.items.add(file);
        });
        this.$refs.file.files = allFiles.files;
      } else {
        const singleFile = new DataTransfer();
        singleFile.items.add(event.dataTransfer.files[0]);
        this.$refs.file.files = singleFile.files;
      }
      this.onChange();
    },
    showFullSize(file, preview) {
      this.fullSize = {
        isVisible: true,
        file,
        preview
      };
    }
  }
};
</script>
<style lang="scss">
// TODO: clean up markup
.fm-file-input {

}
</style>
