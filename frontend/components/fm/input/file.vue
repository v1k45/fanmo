<template>
<div>
  <div
    class="rounded-lg border border-dashed" tabindex="0"
    :class="{ 'border-fm-primary bg-fm-primary-50': isDraggingOver, 'border-gray-300 bg-gray-100': !isDraggingOver }"
    @dragenter.prevent @dragover.prevent="dragover" @dragleave="dragleave" @drop.prevent="drop" @keyup.enter="$refs.file.click();">
    <label class="p-12 relative block cursor-pointer text-center">
      <div>
        <template v-if="multiple">Click here to select files or drag them here.</template>
        <template v-else>Click here to select a file or drag it here.</template>
      </div>
      <input ref="file" type="file" tabindex="-1" :multiple="multiple" v-bind="$attrs" class="w-full h-full top-0 left-0 opacity-0 overflow-hidden cursor-pointer absolute" @change="onChange">
    </label>
  </div>
  <ul v-if="fileList.length" class="flex flex-wrap">
    <li v-for="(file, idx) in fileList" :key="idx" class="relative mt-4 mr-4">
      <img :src="previews[idx]" :alt="file.name" class="h-24 rounded-lg border cursor-pointer" @click="showFullSize(file, previews[idx])">
      <div class="mt-1 h-5 relative">
        <div class="absolute text-sm max-w-full truncate text-gray-500" :title="file.name">{{ file.name }}</div>
      </div>
      <button
        class="absolute -top-1 -right-1 rounded-full bg-fm-error text-white p-0.5 hover:scale-105 transition-transform"
        type="button" title="Remove file" @click="remove(fileList.indexOf(file))">
        <icon-x class="h-4 w-4"></icon-x>
      </button>
    </li>
  </ul>
  <fm-dialog v-model="fullSize.isVisible">
    <template #header>
      <div v-if="fullSize.isVisible" class="truncate">{{ fullSize.file.name }}</div>
    </template>
    <img v-if="fullSize.isVisible" :src="fullSize.preview" :alt="fullSize.file.name" class="w-full">
  </fm-dialog>
</div>
</template>

<script>
export default {
  props: {
    value: { type: [Array, Object, String], default: null },
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
      return this.fileList.map(file => URL.createObjectURL(file));
    }
  },
  methods: {
    onChange() {
      this.fileList = [...this.$refs.file.files];
      this.$emit('input', this.fileList);
    },
    remove(i) {
      const allFiles = new DataTransfer();
      this.fileList.forEach((file, idx) => {
        if (i === idx) return;
        allFiles.items.add(file);
      });
      this.$refs.file.files = allFiles.files;
      this.fileList.splice(i, 1);
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
          allFiles.items.add(file);
        });
        [...event.dataTransfer.files].forEach(file => {
          allFiles.items.add(file);
        });
        this.$refs.file.files = allFiles.files;
      } else this.$refs.file.files = event.dataTransfer.files[0];
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
