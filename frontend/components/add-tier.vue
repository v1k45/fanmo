<template>
<div class="modal" :class="{ 'modal-open': valueLocal }">
  <div class="modal-box flex flex-col p-0" style="max-height: 90vh">
    <div class="p-4 border-b flex items-center">
      <h2 class="text-xl font-semibold">{{ isEditing ? 'Edit tier' : 'Add a tier' }}</h2>
    </div>
    <div class="p-4 overflow-y-auto scrollbar flex-grow">
      <form @submit.prevent>
        <div class="form-control flex-row items-center justify-end">
          <label class="label label-text" :class="{ 'text-primary': !form.is_public }">Private</label>
          <input v-model="form.is_public" type="checkbox" checked="checked" class="toggle toggle-primary mx-2">
          <label class="label label-text" :class="{ 'text-primary': form.is_public }">Public</label>
        </div>

        <div class="form-control">
          <label class="label label-text">Tier name</label>
          <input v-model="form.name" type="text" placeholder="Gold, Silver, Bronze, etc." class="input input-bordered" :class="{ 'input-error': errors.name }" required>
          <label v-for="(error, index) in errors.name" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Monthly price</label>
          <label class="input-group">
            <span><icon-indian-rupee :size="16"></icon-indian-rupee></span>
            <input v-model="form.amount" type="number" class="input input-bordered flex-grow rounded-l-none" :class="{ 'input-error': errors.amount }" required>
          </label>
          <label v-for="(error, index) in errors.amount" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Description</label>
          <textarea v-model="form.description" rows="4" class="textarea textarea-bordered" :class="{ 'textarea-error': errors.description }" required></textarea>
          <label v-for="(error, index) in errors.description" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <div class="form-control mt-3">
          <label class="label label-text">Welcome message</label>
          <textarea v-model="form.welcome_message" rows="4" class="textarea textarea-bordered" :class="{ 'textarea-error': errors.welcome_message }" required></textarea>
          <label v-for="(error, index) in errors.welcome_message" :key="index" class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>
        <!-- <div class="form-control mt-3">
          <label class="label">
            <span class="label-text">Image <span class="text-xs">(optional)</span></span>
          </label>
          <input type="file" class="input input-bordered">
        </div> -->
      </form>
    </div>

    <div class="modal-action p-4 border-t">
      <button class="btn btn-ghost" @click="valueLocal = false;">Cancel</button>
      <button class="btn btn-primary" type="submit" @click="save">
        {{ isEditing ? 'Update tier' : 'Create tier' }}
      </button>
    </div>
  </div>
</div>
</template>

<script>
import cloneDeep from 'lodash/cloneDeep';
import pick from 'lodash/pick';

const initialFormState = () => ({
  name: '',
  amount: '',
  description: '',
  welcome_message: '',
  is_public: true
});

export default {
  props: {
    value: { type: Boolean, required: true },
    tierToUpdate: { type: Object, default: null }
  },
  data() {
    return {
      form: initialFormState(),
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
    },
    isEditing() {
      return !!this.tierToUpdate;
    }
  },
  watch: {
    valueLocal(isVisible) {
      if (!isVisible) {
        this.form = initialFormState();
        this.errors = {};
      } else {
        // eslint-disable-next-line no-lonely-if
        if (this.tierToUpdate) this.form = pick(cloneDeep(this.tierToUpdate), Object.keys(initialFormState()));
      }
    }
  },
  methods: {
    async save() {
      try {
        let createdOrUpdatedTier;
        if (this.isEditing) createdOrUpdatedTier = await this.$axios.$put(`/api/tiers/${this.tierToUpdate.id}/`, this.form);
        else createdOrUpdatedTier = await this.$axios.$post('/api/tiers/', this.form);

        this.$emit('update', createdOrUpdatedTier);
        this.valueLocal = false;
      } catch (err) {
        this.errors = err.response.data;
      }
    }
  }
};
</script>
