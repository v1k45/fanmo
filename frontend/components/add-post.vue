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
          <label class="label label-text">Type</label>
          <select
            v-model="form.content.type"
            type="text"
            class="select select-bordered"
            :class="{ 'input-error': (errors.content && errors.content.type ) }"
            required>
            <option disabled value="">Please select one</option>
            <option value="text">Text</option>
            <option value="link">Link</option>
            <option value="image">Image</option>
          </select>
          <label
            v-for="(error, index) in (errors.content && errors.content.type)"
            :key="index"
            class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>

        <div v-if="form.content.type == 'text'" class="form-control mt-3">
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

        <div v-if="form.content.type == 'link'" class="form-control">
          <label class="label label-text">Link</label>
          <input
            v-model="form.content.link"
            type="text"
            class="input input-bordered"
            :class="{ 'input-error': (errors.content && errors.content.link) }"
            required>
          <label
            v-for="(error, index) in (errors.content && errors.content.link)"
            :key="index"
            class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>

        <div v-if="form.content.type == 'image'" class="form-control mt-3">
          <label class="label label-text">Image</label>
          <div v-if="form.content.image_base64" class="aspect-w-16 aspect-h-9 relative bg-black">
            <img
              class="object-cover h-full w-full absolute"
              :src="form.content.image_base64"
              alt="Post Image">
          </div>
          <input
            type="file"
            class="input input-bordered mt-3"
            :class="{ 'input-error': (errors.content && errors.content.image_base64) }"
            @change="loadImage">
          <label
            v-for="(error, index) in (errors.content && errors.content.image_base64)"
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
            <option value="allowed_tiers">Allowed Tiers</option>
          </select>
          <label
            v-for="(error, index) in errors.visibility"
            :key="index"
            class="label">
            <span class="label-text-alt">{{ error.message }}</span>
          </label>
        </div>

        <div v-if="form.visibility == 'allowed_tiers'" class="form-control mt-3">
          <label class="label label-text">Allowed Tier</label>
          <select
            v-model="form.allowed_tiers"
            type="text"
            class="select select-bordered"
            :class="{ 'input-error': errors.allowed_tiers }"
            multiple
            required>
            <option disabled value="">Select tiers</option>
            <option v-for="tier in $auth.user.tiers" :key="tier.id" :value="tier.id">{{ tier.name }}</option>
          </select>
          <label
            v-for="(error, index) in errors.allowed_tiers"
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
          text: '',
          link: '',
          image_base64: ''
        },
        visibility: 'public',
        allowed_tiers: []
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
    },
    loadImage(event) {
      const image = event.target.files[0];
      const reader = new FileReader();
      reader.readAsDataURL(image);
      reader.onload = loadEvent => {
        this.form.content.image_base64 = loadEvent.target.result;
      };
    }
  }
};
</script>
