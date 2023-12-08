/* eslint no-console: ["warn", { allow: ["error"] }] */
import Vue from 'vue';
import { handleGenericError } from '~/utils';

const SUCCESS = (data) => ({ success: true, data });
const ERROR = (data) => ({ success: false, data });

export const state = () => ({
  postsById: {}, // { [postId]: { ...post } }
  // post detail
  currentPostId: null,

  // profile page
  currentProfileUsername: null, // username for which the data is loaded
  profilePosts_raw: null, // { previous, next, postIds }

  // feed page
  feedPosts_raw: null, // { previous, next, postIds }

  sections_raw: null // { previous, next, reuslts }
});

export const getters = {
  profilePosts(state) {
    if (!state.profilePosts_raw) return {
      notLoaded: true,
      currentProfileUsername: null,
      previous: null,
      next: null,
      results: []
    };
    return {
      currentProfileUsername: state.currentProfileUsername,
      ...state.profilePosts_raw, // previous, next
      results: (state.profilePosts_raw.postIds || []).map(postId => state.postsById[postId]).filter(post => !!post)
    };
  },
  feedPosts(state) {
    if (!state.feedPosts_raw) return {
      notLoaded: true,
      previous: null,
      next: null,
      results: []
    };
    return {
      ...state.feedPosts_raw, // previous, next
      results: (state.feedPosts_raw.postIds || []).map(postId => state.postsById[postId]).filter(post => !!post)
    };
  },
  sections(state) {
    if (!state.sections_raw) return [];
    return state.sections_raw.results;
  },
  sectionsLoaded(state) {
    return !!state.sections_raw;
  },
  currentPost(state) {
    const post = state.postsById[state.currentPostId];
    if (!post) return null;
    return post;
  }
};

export const actions = {
  async loadProfilePosts({ commit }, username) {
    try {
      commit('clearProfilePosts');
      const [pinnedPosts, unpinnedPosts] = (await Promise.allSettled([
        this.$axios.$get(`/api/posts/?creator_username=${username}&is_pinned=true`),
        this.$axios.$get(`/api/posts/?creator_username=${username}&is_pinned=false`)
      ])).map(promise => promise.value);
      const posts = { next: unpinnedPosts.next, previous: unpinnedPosts.previous, results: [...pinnedPosts.results, ...unpinnedPosts.results] };
      commit('setProfilePosts', { username, posts });
      return SUCCESS(posts);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  // eslint-disable-next-line camelcase
  async fetchPosts({ commit }, { creator_username, section_id, section_slug, allowed_tiers, visibility, search, ordering }) {
    commit('clearProfilePosts');

    try {
      const posts = await this.$axios.$get('/api/posts/', {
        params: { creator_username, section_id, section_slug, allowed_tiers, visibility, search, ordering }
      });
      commit('setProfilePosts', { username: creator_username, posts });
      return SUCCESS(posts);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadNextProfilePosts({ commit, state }, username) {
    try {
      const posts = await this.$axios.$get(state.profilePosts_raw.next);
      commit('setNextProfilePosts', { posts });
      return SUCCESS(posts);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadFeedPosts({ commit }) {
    try {
      const posts = await this.$axios.$get('/api/posts/?is_following=true');
      commit('setFeedPosts', { posts });
      return SUCCESS(posts);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadNextFeedPosts({ commit, state }) {
    try {
      const posts = await this.$axios.$get(state.feedPosts_raw.next);
      commit('setNextFeedPosts', { posts });
      return SUCCESS(posts);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadSections({ commit }, username) {
    try {
      const sections = await this.$axios.$get('/api/sections/', { params: { creator_username: username } });
      commit('setSections', { sections });
      return SUCCESS(sections);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadNextSections({ commit, state, dispatch }) {
    try {
      const sections = await this.$axios.$get(state.sections_raw.next);
      commit('setNextSections', { sections });
      if (sections.next) {
        await dispatch('loadNextSections');
      }
      return SUCCESS(sections);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadPost({ commit }, postId) {
    try {
      const post = await this.$axios.$get(`/api/posts/${postId}/`);
      commit('setCurrentPost', { post });
      return SUCCESS(post);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  // create
  async createSection({ dispatch }, payload) {
    try {
      const section = await this.$axios.$post('/api/sections/', payload);
      return SUCCESS(section);
    } catch (err) {
      handleGenericError(err);
      return ERROR(err.response.data);
    }
  },
  async addOrRemoveReaction({ commit, state }, { postId, action, emoji = 'heart' }) {
    try {
      const postStats = await this.$axios.$post(`/api/posts/${postId}/reactions/`, { action, emoji });
      commit('updatePostStats', { postId, stats: postStats });
      return SUCCESS(postStats);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  // update
  async updatePost({ commit, state }, { postId, payload }) {
    try {
      const post = await this.$axios.$patch(`/api/posts/${postId}/`, payload);
      commit('updatePost', post);
      return SUCCESS(post);
    } catch (err) {
      handleGenericError(err, false);
      return ERROR(err.response.data);
    }
  },
  async updateSection({ commit, dispatch }, { sectionId, payload }) {
    try {
      const section = await this.$axios.$patch(`/api/sections/${sectionId}/`, payload);
      commit('updateSection', section);
      return SUCCESS(section);
    } catch (err) {
      handleGenericError(err);
      return ERROR(err.response.data);
    }
  },
  // delete
  async deletePost({ commit, state }, postId) {
    try {
      await this.$axios.$delete(`/api/posts/${postId}/`);
      commit('deletePost', postId);
      return SUCCESS();
    } catch (err) {
      return handleGenericError(err, true);
    }
  },
  async deleteSection({ commit, dispatch }, sectionId) {
    try {
      await this.$axios.$delete(`/api/sections/${sectionId}/`);
      commit('deleteSection', sectionId);
      return SUCCESS();
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  }
};


export const mutations = {
  setProfilePosts(state, { username, posts }) {
    const { previous, next, results } = posts;
    results.forEach(post => {
      Vue.set(state.postsById, post.id, post);
    });
    state.profilePosts_raw = {
      previous,
      next,
      postIds: results.map(p => p.id)
    };
    state.currentProfileUsername = username;
  },
  clearProfilePosts(state) {
    state.profilePosts_raw = null;
  },
  setNextProfilePosts(state, { posts }) {
    const { previous, next, results } = posts;
    results.forEach(post => {
      Vue.set(state.postsById, post.id, post);
      state.profilePosts_raw.postIds.push(post.id);
    });
    Object.assign(state.profilePosts_raw, { previous, next });
  },
  setFeedPosts(state, { posts }) {
    const { previous, next, results } = posts;
    results.forEach(post => {
      Vue.set(state.postsById, post.id, post);
    });
    state.feedPosts_raw = {
      previous,
      next,
      postIds: results.map(p => p.id)
    };
  },
  setNextFeedPosts(state, { posts }) {
    const { previous, next, results } = posts;
    results.forEach(post => {
      Vue.set(state.postsById, post.id, post);
      state.feedPosts_raw.postIds.push(post.id);
    });
    Object.assign(state.feedPosts_raw, { previous, next });
  },
  setSections(state, { sections }) {
    const { previous, next, results } = sections;
    state.sections_raw = {
      previous,
      next,
      results
    };
  },
  setNextSections(state, { sections }) {
    const { previous, next, results } = sections;
    state.sections_raw.results.push(...results);
    Object.assign(state.sections_raw, { previous, next });
  },
  setCurrentPost(state, { post }) {
    state.currentPostId = post.id;
    Vue.set(state.postsById, post.id, post);
  },
  unsetCurrentPost(state) {
    state.currentPostId = null;
  },
  updatePost(state, post) {
    state.postsById[post.id] = post;
  },
  updatePostStats(state, { postId, stats }) {
    state.postsById[postId].stats = stats;
  },
  updatePostUser(state, { postId, user }) {
    state.postsById[postId].author_user = user;
  },
  deletePost(state, postId) {
    Vue.delete(state.postsById, postId);
  },
  updateSection(state, section) {
    const sectionIdx = state.sections_raw.results.findIndex(currSection => currSection.id === section.id);
    state.sections_raw.results.splice(sectionIdx, 1, section);
  },
  deleteSection(state, sectionId) {
    const sectionIdx = state.sections_raw.results.findIndex(currSection => currSection.id === sectionId);
    state.sections_raw.results.splice(sectionIdx, 1);
  }
};
