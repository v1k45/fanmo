<template>
<div>
  <div v-if="profilePosts" class="flex flex-col-reverse xl:flex-row flex-wrap xl:flex-nowrap xl:space-x-8">
    <!-- posts start -->
    <div class="w-full md:max-w-2xl mx-auto md:flex-shrink-0">
      <template v-if="profilePosts">
        <fm-lazy v-for="post in profilePosts.results" :key="post.id" class="mb-6 md:mb-8" min-height="300">
          <profile-post :post="post" show-creator-info @share-click="handleShareClick"></profile-post>
        </fm-lazy>
      </template>
      <div v-if="profilePosts && profilePosts.next" class="text-center mt-4">
        <fm-button :loading="nextPostsLoading" @click="loadNextPostsLocal">Load more</fm-button>
      </div>
      <div v-if="!profilePosts.notLoaded && !profilePosts.results.length" class="text-sm text-gray-500">
        No posts to show here yet.
      </div>
      <div v-if="profilePosts.notLoaded">
        <profile-post-skeleton v-for="n in [1,2,3,4,5]" :key="n"></profile-post-skeleton>
      </div>
      <div v-if="profilePosts.notLoaded && profilePostsLoading" class="text-sm text-gray-500 text-center">
        Loading posts...
      </div>
    <!-- posts end -->
    </div>

    <!-- following users start -->
    <div class="flex-grow min-w-0 mb-6">
      <div class="sticky top-[76px]">
        <!-- filters start -->
        <div class="flex flex-col w-full space-y-4">

          <fm-button type="primary" block @click="addPost.isVisible = true;"><icon-image-plus class="mr-1 -mt-0.5" :size="16"></icon-image-plus> Add a post</fm-button>

          <hr>

          <!-- search start -->
          <div>
            <label class="text-sm block font-bold mb-2">Search for posts</label>
            <fm-input v-model="filter.search" placeholder="Search by post title" @input="handleSearchInput">
              <template #prepend>
                <icon-search class="w-em"></icon-search>
              </template>
            </fm-input>
          </div>
          <!-- search end -->

          <!-- sort start -->
          <div>
            <label class="text-sm block font-bold mb-2">Sort by</label>
            <fm-input v-model="filter.orderBy" type="select" @change="loadPosts">
              <option value="-created_at">Newest post first</option>
              <option value="created_at">Oldest post first</option>
            </fm-input>
          </div>
          <!-- sort end -->

          <!-- section filter start -->
          <div v-if="sections.length">
            <label class="text-sm block font-bold mb-2">Section</label>
            <fm-input v-model="filter.sectionId" type="select" @change="loadPosts">
              <option :value="null">All</option>
              <option v-for="section in sections" :key="section.id" :value="section.id">{{ section.title }}</option>
            </fm-input>
          </div>
          <!-- section filter end -->

          <!-- tier filter start -->
          <div class="flex flex-col space-y-1.5 mb-4">
            <label class="font-medium">Tier</label>
            <fm-input v-model="filter.tier" type="select" @change="loadPosts">
              <option :value="null">All</option>
              <option value="public">Public</option>
              <option value="all_members">All Members</option>
              <option v-for="tier in $auth.user.tiers" :key="tier.id" :value="tier.id">{{ tier.name }}</option>
            </fm-input>
          </div>

        <!-- tier filter end -->

        </div>
      <!-- filters end -->

      </div>
    </div>
  </div>

  <profile-add-post v-model="addPost.isVisible"></profile-add-post>

  <!-- dialogs start -->
  <profile-share v-model="sharePost.isVisible" :text="sharePost.text" :relative-url="sharePost.relativeUrl"></profile-share>
  <!-- dialogs end -->
</div>
</template>


<script>
import debounce from 'lodash/debounce';
import { mapActions, mapGetters } from 'vuex';

export default {
  data() {
    return {
      filter: {
        search: '',
        isActive: null,
        sectionId: null,
        tier: null,
        orderBy: '-created_at'
      },
      profilePostsLoading: false,
      nextPostsLoading: false,
      addPost: {
        isVisible: false
      },
      sharePost: {
        isVisible: false,
        relativeUrl: null,
        text: null
      }
    };
  },
  head: {
    title: 'Posts'
  },
  computed: {
    ...mapGetters('posts', ['profilePosts', 'sections']),
    hasActiveFilters() {
      return !!(this.filter.search || this.filter.isActive !== null);
    }
  },
  created() {
    this.loadPosts();
    this.loadSections(this.$auth.user.username);
    const routeData = (this.$route.params.data || {});
    if (routeData.intent === 'add') {
      this.addPost.isVisible = true;
    }
  },
  methods: {
    ...mapActions('posts', ['fetchPosts', 'loadNextProfilePosts', 'loadSections']),
    async loadPosts() {
      const params = { creator_username: this.$auth.user.username, ordering: this.filter.orderBy };
      if (this.filter.search) {
        params.search = this.filter.search;
      }
      if (this.filter.isActive !== null) {
        params.is_active = this.filter.isActive;
      }
      if (this.filter.sectionId) {
        params.section_id = this.filter.sectionId;
      }

      if (typeof this.filter.tier === 'number') {
        params.allowed_tiers = this.filter.tier;
      } else if (this.filter.tier) {
        params.visibility = this.filter.tier;
      }

      this.profilePostsLoading = true;
      await this.fetchPosts(params);
      this.profilePostsLoading = false;
    },
    handleSearchInput: debounce(function() {
      this.loadPosts();
    }, 250),
    async loadNextPostsLocal() {
      this.nextPostsLoading = true;
      await this.loadNextProfilePosts();
      this.nextPostsLoading = false;
    },
    handleShareClick(post) {
      this.sharePost = {
        isVisible: true,
        relativeUrl: `p/${post.slug}/${post.id}`,
        text: post.title
      };
    }
  }
};
</script>

