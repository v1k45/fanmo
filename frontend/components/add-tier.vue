<template>
<div class="modal" :class="{ 'modal-open': valueLocal }">
  <div class="modal-box flex flex-col p-0" style="max-height: 90vh">
    <div class="p-4 border-b flex items-center">
      <h2 class="text-xl font-semibold">Add a tier</h2>
    </div>
    <div class="p-4 overflow-y-auto scrollbar flex-grow">
      <form @submit.prevent>
        <div class="form-control">
          <label class="label label-text">Tier name</label>
          <input type="text" placeholder="Gold, Silver, Bronze, etc." class="input input-bordered">
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Monthly price</label>
          <div class="flex">
            <div class="px-5 border flex items-center bg-gray-200 rounded-l-lg">
              <icon-indian-rupee :size="16"></icon-indian-rupee>
            </div>
            <input type="number" class="input input-bordered flex-grow rounded-l-none">
          </div>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Description</label>
          <textarea rows="4" class="textarea textarea-bordered"></textarea>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Benefits</label>
          <ol class="list-decimal">
            <li v-for="i in 3" :key="i" class="ml-5 mt-2">
              <input type="text" class="input input-bordered w-full">
            </li>
          </ol>
        </div>
        <div class="form-control mt-3">
          <label class="label">
            <span class="label-text">Image <span class="text-xs">(optional)</span></span>
          </label>
          <input type="file" class="input input-bordered">
        </div>
      </form>
    </div>

    <div class="modal-action p-4 border-t">
      <button class="btn" @click="valueLocal = false;">Cancel</button>
      <button class="btn btn-primary">Create tier</button>
    </div>
  </div>
</div>
</template>

<script>
export default {
  props: {
    value: { type: Boolean, required: true }
  },
  computed: {
    valueLocal: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('input', val);
      }
    }
  }
};
</script>
