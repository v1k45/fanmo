<template>
<div class="container">
  <div v-if="!loading" class="max-w-7xl row gx-0 lg:gx-4 mx-auto flex-wrap-reverse container">
    <div class="col-12 lg:col-8">
      <div>
        <div v-if="profilePosts.notLoaded">
          <profile-post-skeleton v-for="n in [1,2,3,4,5]" :key="n"></profile-post-skeleton>
        </div>
        <div v-if="profilePosts.results.length">
          <profile-post
            v-for="post in profilePosts.results" :key="post.id"
            :post="post" :hide-options="isPreviewMode" class="mb-6 md:mb-8" :join-action-loading="loadingLockedPostId === post.id"
            @share-click="$emit('share', $event)" @subscribe-click="$emit('subscribe', $event, { postId: post.id })">
          </profile-post>
        </div>
        <div v-if="profilePosts.next" class="text-center mt-4">
          <fm-button :loading="postsLoading" @click="$emit('load-more-posts')">Load more</fm-button>
        </div>

        <!-- no posts action start -->
        <fm-card
          v-else-if="isSelfProfile && !profilePosts.results.length"
          class="mx-auto overflow-hidden" body-class="text-center !pt-16 !pb-20">
          <icon-image-plus class="h-16 w-16 stroke-1 animatecss animatecss-tada"></icon-image-plus>
          <div class="mt-2">
            Post exclusive and private content of any type for your fans and keep in touch by interacting with them using comments.
          </div>
          <nuxt-link :to="{ name: 'posts', params: { data: { intent: 'add' } } }">
            <fm-button class="mt-4 min-w-[200px]" type="primary">
              Add a post
            </fm-button>
          </nuxt-link>
        </fm-card>
        <!-- no posts action end -->

        <!-- no posts public start -->
        <div v-else-if="!isSelfProfile && !profilePosts.results.length" class="text-center text-gray-500">
          {{ user.display_name }} hasn't posted anything yet.
        </div>
        <!-- no posts public end -->
      </div>
    </div>
    <div class="col-12 lg:col-4 mb-4 lg:mb-0">
      <div class="overflow-hidden sticky top-20">

        <fm-card v-if="selectedSection" body-class="" class="mb-4">
          <fm-markdown-styled>
            <div v-html="selectedSection.description"></div>
          </fm-markdown-styled>
        </fm-card>
        <fm-card v-else-if="user.about" body-class="" class="mb-4">
          <fm-markdown-styled>
            <div v-html="user.about"></div>
          </fm-markdown-styled>
        </fm-card>

        <div class="text-right md:hidden mb-2">
          <fm-button @click="expandFilters = !expandFilters">
            <icon-filter class="h-em w-em"></icon-filter> Filter
          </fm-button>
        </div>

        <fm-card v-if="sections || isSelfProfile" body-class="" class="mb-4" :class="{ 'hidden md:block': !expandFilters }">
          <template #header>
            Filter
          </template>

          <!-- search start -->
          <div class="flex flex-col space-y-1.5 mb-4">
            <label class="font-medium">Search</label>
            <fm-input v-model="filter.search" placeholder="Search by post title" @input="handleSearchInput">
              <template #prepend>
                <icon-search class="w-em"></icon-search>
              </template>
            </fm-input>
          </div>
          <!-- search end -->

          <div v-if="sections.length" class="flex flex-col space-y-1.5 mb-4">
            <label class="font-medium">Section</label>
            <nuxt-link v-for="section in sections" :key="section.id" :to="{ name: 'username-s-slug', params: { username: user.username, slug: section.slug } }">
              <div class="flex justify-between" :class="{ 'font-semibold': section.slug == $route.params.slug }">
                {{ section.title }}
              </div>
            </nuxt-link>
          </div>

          <div class="flex flex-col space-y-1.5 mb-4">
            <label class="font-medium">Tier</label>
            <a class="cursor-pointer" :class="{ 'font-semibold': filter.tier == null }" @click="filter.tier = null">
              All
            </a>

            <a class="cursor-pointer" :class="{ 'font-semibold': filter.tier === 'public' }" @click="filter.tier = 'public'">
              Public
            </a>

            <a class="cursor-pointer" :class="{ 'font-semibold': filter.tier === 'all_members' }" @click="filter.tier = 'all_members'">
              All Members
            </a>

            <a v-for="tier in user.tiers" :key="tier.id" class="cursor-pointer" :class="{ 'font-semibold': tier.id === filter.tier }" @click="filter.tier = tier.id">
              {{ tier.name }}
            </a>
          </div>

        </fm-card>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import debounce from 'lodash/debounce';
import { mapGetters, mapState, mapActions } from 'vuex';

export default {
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    postsLoading: {
      type: Boolean,
      default: false
    },
    isPreviewMode: {
      type: Boolean,
      default: false
    },
    loadingLockedPostId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      filter: {
        tier: null,
        search: ''
      },
      expandFilters: false
    };
  },
  fetch() {
    if (this.$route.params.slug) {
      this.fetchPosts({ creator_username: this.user.username, section_slug: this.$route.params.slug });
    } else {
      this.loadProfilePosts(this.user.username);
    }
  },
  computed: {
    ...mapGetters('profile', ['isSelfProfile']),
    ...mapGetters('posts', ['profilePosts', 'sections']),
    ...mapState('profile', ['user']),
    selectedSection() {
      return this.sections.find(section => section.slug === this.$route.params.slug);
    }
  },
  watch: {
    'filter.tier': {
      handler() {
        this.loadPosts();
      },
      deep: true
    }
  },
  methods: {
    ...mapActions('posts', ['fetchPosts', 'loadProfilePosts']),
    loadPosts() {
      const params = { creator_username: this.user.username };
      if (this.$route.params.slug) {
        params.section_slug = this.$route.params.slug;
      }

      if (typeof this.filter.tier === 'number') {
        params.allowed_tiers = this.filter.tier;
      } else if (this.filter.tier) {
        params.visibility = this.filter.tier;
      }

      if (this.filter.search) {
        params.search = this.filter.search;
      }

      this.fetchPosts(params);
    },
    handleSearchInput: debounce(function() {
      this.loadPosts();
    }, 250)
  }
};
</script>

