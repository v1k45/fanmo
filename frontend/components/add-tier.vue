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
          <input type="text" placeholder="Gold, Silver, Bronze, etc." v-model="form.name" class="input input-bordered" :class="{ 'input-error': errors.name }" required>
          <label v-for="(error, index) in errors.name" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Monthly price</label>
          <div class="flex">
            <div class="px-5 border flex items-center bg-gray-200 rounded-l-lg">
              <icon-indian-rupee :size="16"></icon-indian-rupee>
            </div>
            <input type="number" class="input input-bordered flex-grow rounded-l-none" v-model="form.amount" :class="{ 'input-error': errors.amount }" required>
          </div>
          <label v-for="(error, index) in errors.amount" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Description</label>
          <textarea rows="4" class="textarea textarea-bordered" v-model="form.description" :class="{ 'textarea-error': errors.description }" required></textarea>
          <label v-for="(error, index) in errors.description" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Welcome message</label>
          <textarea rows="4" class="textarea textarea-bordered" v-model="form.welcome_message" :class="{ 'textarea-error': errors.welcome_message }" required></textarea>
          <label v-for="(error, index) in errors.welcome_message" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Benefits</label>
          <ol class="list-decimal">
            <li v-for="(benefit, index) in form.benefits" :key="index" class="ml-5 mt-2">
              <input v-model="form.benefits[index]" type="text" class="input input-bordered w-full">
            </li>
          </ol>
          <label v-for="(error, index) in errors.benefits" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
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
      <button class="btn btn-primary" type="submit" @click="save">Create tier</button>
    </div>
  </div>
</div>
</template>

<script>
export default {
  props: {
    value: { type: Boolean, required: true }
  },
  data() {
    return {
      form: {
        name: '',
        amount: '',
        description: '',
        welcome_message: '',
        benefits: ['', '', ''],
        is_public: true
      },
      errors: {}
    };
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
  },
  methods: {
    async save() {
      try {
        await this.$axios.$post('/api/tiers/', this.form);
        this.valueLocal = false;
      } catch (err) {
        this.errors = err.response.data;
      }
    }
  }
};
</script>
