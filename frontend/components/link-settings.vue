<template>
<div class="max-w-md mt-4">
  <form @submit.prevent="save">

    <error-alert :errors="errors"></error-alert>

    <div class="form-control">
      <label class="label label-text">Website</label>
      <input
        v-model="form.website_url"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.website_url }">
      <label
        v-for="(error, index) in errors.website_url"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">YouTube</label>
      <input
        v-model="form.youtube_url"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.youtube_url }">
      <label
        v-for="(error, index) in errors.youtube_url"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Facebook</label>
      <input
        v-model="form.facebook_url"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.facebook_url }">
      <label
        v-for="(error, index) in errors.facebook_url"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>

    <div class="form-control mt-3">
      <label class="label label-text">Instagram</label>
      <input
        v-model="form.instagram_url"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.instagram_url }">
      <label
        v-for="(error, index) in errors.instagram_url"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
      </label>
    </div>


    <div class="form-control mt-3">
      <label class="label label-text">Twitter</label>
      <input
        v-model="form.twitter_url"
        type="text"
        class="input input-bordered"
        :class="{ 'input-error': errors.twitter_url }">
      <label
        v-for="(error, index) in errors.twitter_url"
        :key="index"
        class="label">
        <span class="label-text-alt">{{ error.message }}</span>
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
        website_url: this.$auth.user.social_links.website_url,
        youtube_url: this.$auth.user.social_links.youtube_url,
        facebook_url: this.$auth.user.social_links.facebook_url,
        instagram_url: this.$auth.user.social_links.instagram_url,
        twitter_url: this.$auth.user.social_links.twitter_url
      },
      errors: {}
    };
  },
  methods: {
    async save() {
      this.errors = {};

      try {
        const updatedUser = await this.$axios.$patch('/api/me/', { social_links: this.form });
        this.$auth.setUser(updatedUser);
      } catch (err) {
        this.errors = err.response.data.social_links;
      }
    }
  }
};
</script>
