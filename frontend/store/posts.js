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
  feedPosts_raw: null // { previous, next, postIds }
});

export const getters = {
  profilePosts(state) {
    if (!state.profilePosts_raw) return {
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
  currentPost(state) {
    const post = state.postsById[state.currentPostId];
    if (!post) return null;
    return post;
  }
};

export const actions = {
  async loadProfilePosts({ commit }, username) {
    try {
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
  // delete
  async deletePost({ commit, state }, postId) {
    try {
      await this.$axios.$delete(`/api/posts/${postId}/`);
      commit('deletePost', postId);
      return SUCCESS();
    } catch (err) {
      return handleGenericError(err, true);
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
  }
};
