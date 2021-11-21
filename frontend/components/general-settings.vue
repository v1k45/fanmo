<template>
<div class="max-w-md mt-4">
  <form @submit.prevent="save">

    <error-alert :errors="errors"></error-alert>

    <div class="form-control">
      <label class="label label-text">Name</label>
      <input
        v-model="form.name"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.name }"
        required>
      <label
        v-for="(error, index) in errors.name"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Username</label>
      <input
        v-model="form.username"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.username }"
        required>
      <label
        v-for="(error, index) in errors.username"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Avatar</label>
      <div class="avatar">
        <div class="w-32 h-32 rounded-full">
          <img :src="avatarUrl">
        </div>
      </div>
      <input
        type="file"
        class="input input-bordered mt-3"
        :class="{ 'input-error': errors.avatar_base64 }"
        @change="loadImage($event, 'avatar_base64')">
      <label
        v-for="(error, index) in errors.avatar_base64"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Cover</label>
      <div v-if="coverUrl" class="aspect-w-16 aspect-h-3 relative bg-black">
        <img
          class="object-cover h-full w-full absolute"
          :src="coverUrl"
          alt="Cover photo">
      </div>
      <input
        type="file"
        class="input input-bordered mt-3"
        :class="{ 'input-error': errors.cover_base64 }"
        @change="loadImage($event, 'cover_base64')">
      <label
        v-for="(error, index) in errors.cover_base64"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">About</label>
      <textarea
        v-model="form.about"
        class="textarea textarea-bordered"
        :class="{ 'textarea-error': errors.about }"
        placeholder="Write something down...">
        </textarea>
      <label
        v-for="(error, index) in errors.about"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.about }}</span>
      </label>
    </div>

    <button class="mt-4 btn btn-block btn-success">Save</button>
  </form>
</div>
</template>

<script>
import errorAlert from './ui/error-alert.vue';
export default {
  components: { errorAlert },
  data() {
    return {
      form: {
        name: this.$auth.user.name,
        username: this.$auth.user.username,
        about: this.$auth.user.about,
        avatar_base64: '',
        cover_base64: ''
      },
      errors: {}
    };
  },
  computed: {
    avatarUrl() {
      return this.form.avatar_base64 || this.$auth.user.avatar.medium;
    },
    coverUrl() {
      return this.form.cover_base64 || this.$auth.user.cover.medium;
    }
  },
  methods: {
    async save() {
      this.errors = {};

      // do not include images in payload to prevent clearing it.
      const payload = this.form;
      if (payload.avatar_base64 === '') {
        delete payload.avatar_base64;
      }
      if (payload.cover_base64 === '') {
        delete payload.cover_base64;
      }

      try {
        const updatedUser = await this.$axios.$patch('/api/me/', payload);
        this.$auth.setUser(updatedUser);
      } catch (err) {
        this.errors = err.response.data;
      }
    },
    loadImage(event, fieldName) {
      const image = event.target.files[0];
      const reader = new FileReader();
      reader.readAsDataURL(image);
      reader.onload = loadEvent => {
        this.form[fieldName] = loadEvent.target.result;
      };
    }
  }
};
</script>
