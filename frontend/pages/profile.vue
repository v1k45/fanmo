<template>
<div v-if="user">
  <profile-above-the-tab></profile-above-the-tab>

  <div class="container">
    <fm-tabs v-model="activeTab" class="mt-8">
      <fm-tabs-pane :id="tabName.HOME" label="Home" class="grid grid-cols-12 gap-5 pb-10">
        <div class="col-span-12 md:col-span-7">
          <fm-card body-class="bg-gray-100 text-gray-600" class="overflow-hidden">
            <fm-read-more v-if="user.about" lines="6" class="mb-4">
              <p v-html="user.about"></p>
            </fm-read-more>
            <div class="flex justify-center space-x-4 text-gray-600">
              <a v-if="user.social_links.website_url" class="unstyled hover:text-gray-800" title="Website" target="_blank" :href="user.social_links.website_url">
                <icon-globe :size="24"></icon-globe>
              </a>
              <a v-if="user.social_links.twitter_url" class="unstyled hover:text-gray-800" title="Twitter" target="_blank" :href="user.social_links.twitter_url">
                <icon-twitter :size="24"></icon-twitter>
              </a>
              <a v-if="user.social_links.youtube_url" class="unstyled hover:text-gray-800" title="Youtube" target="_blank" :href="user.social_links.youtube_url">
                <icon-youtube :size="24"></icon-youtube>
              </a>
              <a v-if="user.social_links.instagram_url" class="unstyled hover:text-gray-800" title="Instagram" target="_blank" :href="user.social_links.instagram_url">
                <icon-instagram :size="24"></icon-instagram>
              </a>
              <a v-if="user.social_links.facebook_url" class="unstyled hover:text-gray-800" title="Facebook" target="_blank" :href="user.social_links.facebook_url">
                <icon-facebook :size="24"></icon-facebook>
              </a>
            </div>
          </fm-card>

          <div class="mt-8">
            <div class="flex flex-wrap items-center">
              <h1 class="text-2xl font-bold mr-auto">Posts</h1>
              <button v-if="$auth.loggedIn && user.username == $auth.user.username" class="mt-4 sm:mt-0 btn btn-wide btn-black" @click="isAddPostVisible = true;">
                <IconPlus class="mr-1" :size="16"></IconPlus>
                Add a post
              </button>
            </div>
            <div v-if="posts && posts.count" class="mt-8">
              <post v-for="post in posts.results" :key="post.id" :post="post" class="mb-6"></post>
            </div>
          </div>
        </div>
        <div class="col-span-12 md:col-span-5">
          <donation-form :user="user" @donated="prependDonation"></donation-form>
          <div v-if="donations && donations.count">
            <div>
              <donation v-for="donation in donations.results" :key="donation.id" :donation="donation">
              </donation>
            </div>
          </div>
        </div>
      </fm-tabs-pane>

      <fm-tabs-pane :id="tabName.TIERS" label="Memberships" class="row justify-center pb-10">
        <tier
          v-for="tier in user.tiers"
          :key="tier.id"
          :user="user"
          :tier="tier"></tier>
      </fm-tabs-pane>

      <fm-tabs-pane :id="tabName.DONATIONS" label="Donations" class="row justify-end pb-10">
        <div v-if="donations && donations.count" class="col-12 md:col-6">
          <div class="row justify-center">
            <donation v-for="donation in donations.results" :key="donation.id" :donation="donation">
            </donation>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="row justify-center">
            <donation-form :user="user" @donated="prependDonation"></donation-form>
          </div>
        </div>
      </fm-tabs-pane>
    </fm-tabs>
  </div>


  <add-post v-model="isAddPostVisible" @created="prependPost"></add-post>
</div>
</template>

<script>
import {
  Plus as IconPlus
} from 'lucide-vue';
import { mapActions, mapGetters, mapState } from 'vuex';

export default {
  components: {
    IconPlus
  },
  layout:
    'default-no-container',
  props: {
    username: {
      type: String,
      default: null
    }
  },
  data() {
    const tabName = {
      HOME: 'home',
      TIERS: 'tiers',
      DONATIONS: 'donations'
    };
    return {
      tabName,
      activeTab: tabName.HOME,
      isAddPostVisible: false
    };
  },
  async fetch() {
    const username = this.username || this.$auth.user.username;
    await this.fetchProfile(username);
  },
  head: {
    title: 'My profile'
  },
  computed: {
    ...mapState('profile', ['user', 'donations', 'posts']),
    ...mapGetters('profile', ['isSelfProfile'])
  },
  methods: {
    ...mapActions('profile', ['fetchProfile']),

    prependPost(post) {
      this.posts.results.unshift(post);
    },
    prependDonation(donation) {
      this.donations.results.unshift(donation);
    }
  }
};
</script>
