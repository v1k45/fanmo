<template>
<div>
  <div class="absolute z-10 flex space-x-4" :class="{ 'top-1 right-1': !user.cover && !isSelfProfile, 'top-1 right-1 md:top-5 md:right-10': user.cover || isSelfProfile }">
    <fm-button v-if="isSelfProfile" class="hidden md:block" @click="$emit('add-post')">
      <icon-image-plus class="mr-1 -mt-0.5" :size="16"></icon-image-plus>
      Add a post
    </fm-button>
    <fm-button v-if="isSelfProfile" class="hidden md:block" @click="openEditDialog">
      <icon-wand class="" :size="16"></icon-wand>
      Edit page
    </fm-button>
    <layout-navigation class="inline-block" :type="$auth.loggedIn ? 'hamburger-minimal' : 'anonymous-hamburger'"></layout-navigation>
  </div>

  <!-- cover photo start -->
  <div class="relative bg-gray-200 border-b">
    <div v-if="user.cover" class="aspect-w-16 aspect-h-5 lg:aspect-h-3">
      <img
        class="object-cover h-full w-full absolute"
        :src="user.cover.big"
        alt="Cover photo">
    </div>
    <div v-else-if="isSelfProfile" class="aspect-w-16 aspect-h-5 lg:aspect-h-3"></div>


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
      <fm-avatar :src="user.avatar && user.avatar.medium" :name="user.display_name" size="w-24 h-24 lg:w-32 lg:h-32"></fm-avatar>

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
      <div class="mx-auto lg:mr-0 text-center lg:text-left lg:ml-3">
        <div class="text-2xl text-black font-bold">{{ user.name || user.username }}</div>
        <div v-if="user.one_liner" class="mt-1 text-gray-500">
          {{ user.one_liner }}
        </div>
      </div>
      <!-- name and short description end -->

      <!-- share and follow/unfollow actions start -->
      <div class="mx-auto lg:mr-[unset] lg:ml-auto my-4 lg:my-0 flex items-center">

        <fm-button class="mr-4 inline-flex items-center" @click="isProfileShareVisible = true;">
          <icon-share class="inline-block -mt-0.5 mr-1 h-em w-em"></icon-share> Share
        </fm-button>

        <fm-button :type="user.is_following ? 'success' : 'primary'" class="w-36" :loading="isFollowLoading" @click="toggleFollow">
          <div v-if="user.is_following" class="flex items-center justify-center">
            <icon-check class="inline-block mr-1 h-em w-em"></icon-check> Following
          </div>
          <div v-else class="flex items-center justify-center">
            <icon-plus class="inline-block mr-1 h-em w-em"></icon-plus> Follow
          </div>
        </fm-button>

        <fm-button v-if="isSelfProfile" v-tooltip="'View your page as it would appear to your supporters'" class="ml-4 inline-block w-[42px] !px-0 !rounded-full" @click="setPreviewMode(true)">
          <icon-eye class="inline-block h-4 w-4"></icon-eye>
        </fm-button>
        <fm-alert v-else-if="isPreviewMode" type="warning" class="fixed bottom-[78px] md:bottom-0 w-full left-0 z-20 !rounded-none" :show-icon="false">
          <div class="text-center">
            <span class="hidden sm:inline">You're viewing your page as a supporter.</span>
            <span class="sm:hidden">Viewing as supporter.</span>
            <fm-button type="error" class="ml-4" size="sm" @click="setPreviewMode(false)">Exit view</fm-button>
          </div>
        </fm-alert>
      </div>
      <!-- share and follow/unfollow actions end -->

      <div v-if="isSelfProfile" class="md:hidden text-center space-x-4 w-full">
        <fm-button @click="$emit('add-post')">
          <icon-image-plus class="mr-1 -mt-0.5" :size="16"></icon-image-plus>
          Add a post
        </fm-button>
        <fm-button @click="openEditDialog">
          <icon-wand class="" :size="16"></icon-wand>
          Edit page
        </fm-button>
      </div>

    </div>

  </div>
  <!-- avatar, name, short description, actions end -->


  <fm-dialog v-model="isEditing" require-explicit-close>
    <template #header>Edit page</template>

    <fm-form id="editProfileForm" :errors="editFormErrors" @submit.prevent="saveEditForm">
      <fm-input v-model="editForm.name" uid="name" type="text" label="Page name" autofocus required>
        <template #label>
          <div class="flex">
            Page name

            <button v-tooltip="'To change your username, go to account settings.'" type="button" class="ml-auto">
              <icon-info class="h-em w-em"></icon-info>
            </button>
          </div>
        </template>
      </fm-input>
      <fm-input v-model="editForm.one_liner" uid="one_liner" type="text" label="What are you creating?" placeholder="is creating space documentaries"></fm-input>
      <fm-input-rich v-model="editForm.about" uid="about" label="About"></fm-input-rich>

      <label class="block mt-8">Social links <small>(leave empty to hide)</small></label>

      <div class="text-sm text-gray-500 mt-2">Social links will be hidden from public if About is not set.</div>

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

  <profile-share
    v-if="user"
    v-model="isProfileShareVisible"
    text="Support me on Fanmo!"
    :relative-url="user.username">
  </profile-share>

</div>
</template>

<script>
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
import {
  Check as IconCheck,
  Plus as IconPlus,
  Camera as IconCamera,
  Globe as IconGlobe
} from 'lucide-vue';
import get from 'lodash/get';
import FmInputRich from '~/components/fm/input/rich.vue';

export default {
  components: {
    IconCheck,
    IconPlus,
    IconCamera,
    IconGlobe,
    FmInputRich
  },
  data() {
    return {
      isProfileShareVisible: false,
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
      editFormErrors: {},
      isFollowLoading: false,
      showStickyNav: false
    };
  },
  computed: {
    ...mapState('profile', ['user', 'isPreviewMode']),
    ...mapGetters('profile', ['isSelfProfile'])
  },
  watch: {
    isEditing(isEditing) {
      if (!isEditing) this.resetEditDialog();
    }
  },
  beforeDestroy() {
    this.setPreviewMode(false);
  },
  methods: {
    ...mapActions('profile', ['updateUser', 'follow', 'unfollow']),
    ...mapMutations('profile', ['setPreviewMode']),

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
        this.$refs.coverInput.value = '';
      }
      const { success, data } = await this.updateUser({ payload });
      if (!success) {
        if (get(data, 'cover_base64[0]')) this.$toast.error(data.cover_base64[0].message);
        else this.$toast.error(data);
        this.$refs.coverInput.value = '';
      }
    },

    async handleAvatarChange(evt) {
      const payload = {};
      if (evt) {
        if (!evt.target.files[0]) return;
        payload.avatar_base64 = await this.getBase64(evt.target.files[0]);
      } else {
        payload.avatar_base64 = '';
        this.$refs.avatarInput.value = '';
      }

      const { success, data } = await this.updateUser({ payload });
      if (!success) {
        if (get(data, 'avatar_base64[0]')) this.$toast.error(data.avatar_base64[0].message);
        else this.$toast.error(data);
        this.$refs.avatarInput.value = '';
      }
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


    async toggleFollow() {
      // TODO: redirect back to this after login and dispatch follow automatically
      if (!this.$auth.loggedIn) return this.$router.push('/login');
      this.isFollowLoading = true;
      if (this.user.is_following) await this.unfollow();
      else await this.follow();
      this.isFollowLoading = false;
    }
  }
};
</script>

<style>

</style>
