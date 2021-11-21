<template>
<div class="modal" :class="{ 'modal-open': valueLocal }">
  <div class="modal-box flex flex-col p-0" style="max-height: 90vh">
    <div class="p-4 border-b flex items-center">
      <h2 class="text-xl font-semibold">Add a post</h2>
    </div>
    <div class="p-4 overflow-y-auto scrollbar flex-grow">
      <form @submit.prevent>
        <error-alert :errors="errors"></error-alert>
        <div class="form-control">
          <label class="label label-text">Title</label>
          <input
            v-model="form.title"
            type="text"
            class="input input-bordered"
            :class="{ 'input-error': errors.title }"
            required>
          <label
            v-for="(error, index) in errors.title"
            :key="index"
            class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>

        <div class="form-control">
          <label class="label label-text">Post</label>
          <textarea
            v-model="form.content.text"
            class="textarea textarea-bordered"
            :class="{ 'textarea-error': (errors.content && errors.content.text) }"
            placeholder="Write something down..."
            required>
        </textarea>
          <label
            v-for="(error, index) in (errors.content && errors.content.text)"
            :key="index"
            class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>

        <div class="form-control mt-3">
          <label class="label label-text">Visibility</label>
          <select
            v-model="form.visibility"
            type="text"
            class="select select-bordered"
            :class="{ 'input-error': errors.visibility }"
            required>
            <option disabled value="">Please select one</option>
            <option value="public">Public</option>
            <option value="all_members">All Members</option>
            <option value="minimum_tier">Minimum Tier</option>
          </select>
          <label
            v-for="(error, index) in errors.visibility"
            :key="index"
            class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>

        <div v-if="form.visibility == 'minimum_tier'" class="form-control mt-3">
          <label class="label label-text">Minimum Tier</label>
          <select
            v-model="form.minimum_tier"
            type="text"
            class="select select-bordered"
            :class="{ 'input-error': errors.minimum_tier }"
            required>
            <option disabled value="">Please select one</option>
            <option v-for="tier in $auth.user.tiers" :key="tier.id" :value="tier.id">{{ tier.name }}</option>
          </select>
          <label
            v-for="(error, index) in errors.minimum_tier"
            :key="index"
            class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>

      </form>
    </div>

    <div class="modal-action p-4 border-t">
      <button class="btn" @click="valueLocal = false;">Cancel</button>
      <button class="btn btn-primary" type="submit" @click="save">Create post</button>
    </div>
  </div>
</div>
</template>

<script>
import errorAlert from './ui/error-alert.vue';
export default {
  components: { errorAlert },
  props: {
    value: { type: Boolean, required: true }
  },
  data() {
    return {
      form: {
        title: '',
        content: {
          type: 'text',
          text: ''
        },
        visibility: 'public',
        minimum_tier: ''
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
        const post = await this.$axios.$post('/api/posts/', this.form);
        this.valueLocal = false;
        this.$emit('created', post);
      } catch (err) {
        this.errors = err.response.data;
      }
    }
  }
};
</script>
