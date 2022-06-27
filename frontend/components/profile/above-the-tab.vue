<template>
<div>
  <!-- cover photo start -->
  <div class="relative bg-gray-200 border-b">
    <div v-if="user.cover" class="aspect-w-16 aspect-h-4 lg:aspect-h-3">
      <img
        class="object-cover h-full w-full absolute"
        :src="user.cover.big"
        alt="Cover photo">
    </div>
    <div v-else-if="isSelfProfile" class="aspect-w-16 aspect-h-4 lg:aspect-h-3"></div>


    <!-- actions icon start -->
    <div v-if="isSelfProfile" class="absolute z-10 left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
      <input v-show="false" ref="coverInput" type="file" accept="image/*" @change="handleCoverChange">
      <fm-dropdown>
        <button class="rounded-full bg-gray-300 hover:bg-gray-400 p-4" title="Cover picture options">
          <icon-camera></icon-camera>
        </button>
        <template #items>
          <fm-dropdown-item v-if="!user.cover" @click="$refs.coverInput.click()">Set cover picture</fm-dropdown-item>
          <template v-else>
            <fm-dropdown-item @click="$refs.coverInput.click()">Update</fm-dropdown-item>
            <fm-dropdown-item class="text-fm-error" @click="handleCoverChange(false)">Remove</fm-dropdown-item>
          </template>
        </template>
      </fm-dropdown>
    </div>
  <!-- actions icon end -->
  </div>
  <!-- cover photo end -->

  <!-- avatar, name, short description, actions start -->
  <div class="container flex flex-col lg:flex-row items-center lg:items-start pt-3 lg:pt-6">

    <!-- avatar start -->
    <div
      class="lg:z-10 rounded-t-full p-1 bg-white border-1 lg:border-2 border-white flex-shrink-0 relative"
      :class="{
        'lg:-mt-16': user.cover && !user.one_liner && !isSelfProfile,
        'lg:-mt-12': isSelfProfile || (user.cover && user.one_liner)
      }">
      <fm-avatar :src="user.avatar && user.avatar.medium" :name="user.name" :username="user.username" size="w-24 h-24 lg:w-32 lg:h-32"></fm-avatar>

      <!-- actions icon start -->
      <div v-if="isSelfProfile" class="absolute bottom-4 -right-2">
        <input v-show="false" ref="avatarInput" type="file" accept="image/*" @change="handleAvatarChange">
        <fm-dropdown>
          <button class="rounded-full bg-gray-300 hover:bg-gray-400 p-3" title="Profile picture options">
            <icon-camera :size="22"></icon-camera>
          </button>
          <template #items>
            <fm-dropdown-item v-if="!user.avatar" @click="$refs.avatarInput.click()">Set profile picture</fm-dropdown-item>
            <template v-else>
              <fm-dropdown-item @click="$refs.avatarInput.click()">Update</fm-dropdown-item>
              <fm-dropdown-item class="text-fm-error" @click="handleAvatarChange(false)">Remove</fm-dropdown-item>
            </template>
          </template>
        </fm-dropdown>
      </div>
      <!-- actions icon end -->
    </div>
    <!-- avatar end -->

    <div class="flex flex-col lg:flex-row flex-grow items-start" :class="{ 'self-stretch items-center': !user.cover }">
      <!-- name and short description start -->
      <div class="text-center lg:text-left lg:ml-3">
        <div class="text-2xl text-black font-bold">{{ user.name || user.username }}</div>
        <div v-if="user.one_liner" class="mt-1 text-gray-500">
          {{ user.one_liner }}
        </div>
        <fm-button v-if="isSelfProfile" class="mt-3" @click="openEditDialog">Edit page</fm-button>
      </div>
      <!-- name and short description end -->

      <!-- Donate and follow/unfollow actions start -->
      <div class="ml-auto my-4 lg:my-0">
        <fm-button type="primary" class="mr-4 inline-flex items-center mr-0">
          <!-- TODO: update image -->
          <logo circle class="h-4 mr-2 inline-block"></logo> Support
        </fm-button>
        <fm-button :type="user.is_following ? 'success' : ''" class="w-36" @click="toggleFollow">
          <div v-if="user.is_following" class="flex items-center justify-center">
            <icon-check class="inline-block mr-1 h-em w-em"></icon-check> Following
          </div>
          <div v-else class="flex items-center justify-center">
            <icon-plus class="inline-block mr-1 h-em w-em"></icon-plus> Follow
          </div>
        </fm-button>
      </div>
    <!-- Donate and follow/unfollow actions end -->
    </div>

  </div>
  <!-- avatar, name, short description, actions end -->


  <fm-dialog v-model="isEditing">
    <template #header>Edit page</template>

    <fm-form id="editProfileForm" :errors="editFormErrors" @submit.prevent="saveEditForm">
      <fm-input v-model="editForm.name" uid="name" type="text" label="Page name" autofocus required></fm-input>
      <fm-input v-model="editForm.one_liner" uid="one_liner" type="text" label="What are you creating?" placeholder="is creating space documentaries"></fm-input>
      <fm-input v-model="editForm.about" uid="about" type="rich" label="About you"></fm-input>

      <label class="block mt-8">Social links <small>(leave empty to hide)</small></label>

      <div class="flex mt-5 items-center">
        <div class="mr-4 flex-shrink-0"><icon-globe class="text-fm-info"></icon-globe></div>
        <div class="flex-grow"><fm-input v-model="editForm.social_links.website_url" uid="social_links.website_url" placeholder="Website"></fm-input></div>
      </div>
      <div class="flex mt-5 items-center">
        <div class="mr-4 flex-shrink-0"><icon-twitter class="text-sky-500 fill-current"></icon-twitter></div>
        <div class="flex-grow"><fm-input v-model="editForm.social_links.twitter_url" uid="social_links.twitter_url" placeholder="Twitter"></fm-input></div>
      </div>
      <div class="flex mt-5 items-center">
        <div class="mr-4 flex-shrink-0"><icon-youtube class="text-red-500"></icon-youtube></div>
        <div class="flex-grow"><fm-input v-model="editForm.social_links.youtube_url" uid="social_links.youtube_url" placeholder="YouTube"></fm-input></div>
      </div>
      <div class="flex mt-5 items-center">
        <div class="mr-4 flex-shrink-0"><icon-instagram class="text-purple-500"></icon-instagram></div>
        <div class="flex-grow"><fm-input v-model="editForm.social_links.instagram_url" uid="social_links.instagram_url" placeholder="Instagram"></fm-input></div>
      </div>
      <div class="flex mt-5 items-center">
        <div class="mr-4 flex-shrink-0"><icon-facebook class="text-blue-500 fill-current"></icon-facebook></div>
        <div class="flex-grow"><fm-input v-model="editForm.social_links.facebook_url" uid="social_links.facebook_url" placeholder="Facebook"></fm-input></div>
      </div>
    </fm-form>


    <template #footer>
      <div class="text-right">
        <fm-button @click="isEditing = false;">Close</fm-button>
        <fm-button native-type="submit" form="editProfileForm" type="primary">Save</fm-button>
      </div>
    </template>
  </fm-dialog>

</div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import {
  Check as IconCheck,
  Plus as IconPlus,
  Camera as IconCamera,
  Globe as IconGlobe
} from 'lucide-vue';

export default {
  components: {
    IconCheck,
    IconPlus,
    IconCamera,
    IconGlobe
  },
  data() {
    return {
      isEditing: false,
      editForm: {
        name: '',
        about: '',
        one_liner: '',
        social_links: {
          facebook_url: '',
          instagram_url: '',
          twitter_url: '',
          website_url: '',
          youtube_url: ''
        }
      },
      editFormErrors: {}
    };
  },
  computed: {
    ...mapState('profile', ['user']),
    ...mapGetters('profile', ['isSelfProfile'])
  },
  watch: {
    isEditing(isEditing) {
      if (!isEditing) this.resetEditDialog();
    }
  },
  methods: {
    ...mapActions('profile', ['updateUser', 'follow', 'unfollow']),

    async getBase64(file) {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      const fileReaderResult = await new Promise(resolve => {
        reader.onload = loadEvent => resolve(loadEvent);
      });
      return fileReaderResult.target.result;
    },

    async handleCoverChange(evt) {
      const payload = {};
      if (evt) {
        if (!evt.target.files[0]) return;
        payload.cover_base64 = await this.getBase64(evt.target.files[0]);
      } else {
        payload.cover_base64 = '';
      }
      this.updateUser({ payload, handleAll: true });
    },

    async handleAvatarChange(evt) {
      const payload = {};
      if (evt) {
        if (!evt.target.files[0]) return;
        payload.avatar_base64 = await this.getBase64(evt.target.files[0]);
      } else {
        payload.avatar_base64 = '';
      }

      this.updateUser({ payload, handleAll: true });
    },

    openEditDialog() {
      this.isEditing = true;
      this.editForm = {
        name: this.user.name,
        about: this.user.about,
        one_liner: this.user.one_liner,
        social_links: {
          facebook_url: this.user.social_links.facebook_url,
          instagram_url: this.user.social_links.instagram_url,
          twitter_url: this.user.social_links.twitter_url,
          website_url: this.user.social_links.website_url,
          youtube_url: this.user.social_links.youtube_url
        }
      };
    },
    resetEditDialog() {
      this.editForm = {
        name: '',
        about: '',
        one_liner: '',
        social_links: {
          facebook_url: '',
          instagram_url: '',
          twitter_url: '',
          website_url: '',
          youtube_url: ''
        }
      };
      this.editFormErrors = {};
    },

    async saveEditForm() {
      if (this.editForm.about && /^(<p>\s*<\/p>)+$/.test(this.editForm.about.trim())) this.editForm.about = '';
      const { success, data } = await this.updateUser({ payload: this.editForm });
      if (!success) this.editFormErrors = data;
      else {
        this.$toast.success('Your profile information has been saved successfully.');
        this.editFormErrors = {};
      }
    },


    toggleFollow() {
      // TODO: redirect to login for unauthenticated users
      if (this.user.is_following) this.unfollow();
      else this.follow();
    }
  }
};
</script>

<style>

</style>
