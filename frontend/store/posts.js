/* eslint no-console: ["warn", { allow: ["error"] }] */
import Vue from 'vue';
import get from 'lodash/get';
import toast from '~/components/fm/alert/service';

const ERRORED = true;

const SUCCESS = (data) => ({ success: true, data });
const ERROR = (data) => ({ success: false, data });

export const state = () => ({
  postsById: {}, // { [postId]: { ...post } }
  commentsById: {}, // { [commentId]: comment }
  postCommentsMap: {}, // { [postId]: { previous, next, commentIds: [] } }

  // post detail
  currentPostId: null,

  // profile page
  currentProfileUsername: null, // username for which the data is loaded
  profilePosts_raw: null, // { previous, next, postIds }

  // feed page
  feedPosts_raw: null // { previous, next, postIds }
});

const handleGenericError = (err, handleAll = false) => {
  if (process.env.NODE_ENV !== 'production') console.error(err);
  if (err.response.status >= 500) {
    console.error(err);
    toast.error("Internal server error. It's not you, it's us. Please try again in a minute.");
  } else if (err.response.status >= 400) {
    if (handleAll) toast.error(err.response.data);
    else return err.response.data;
  } else if (get(err, 'response.data')) { // shouldn't come here
    console.error(err);
    toast.error(err.response.data);
  } else {
    console.error(err);
    toast.error("We're sorry but an unknown error occurred. If this persists, please contact support.");
  }
  return ERRORED;
};

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
    return {
      ...post,
      comments: get(state.postCommentsMap, `${post.id}.commentIds`, [])
        .map(commentId => state.commentsById[commentId])
        .filter(comment => !!comment),
      hasMoreComments: get(state.postCommentsMap, `${post.id}.next`, false)
    };
  }
};

export const actions = {
  async loadProfilePosts({ commit }, username) {
    try {
      const posts = await this.$axios.$get(`/api/posts/?creator_username=${username}`);
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

  async loadComments({ commit, state }, postId) {
    try {
      const comments = await this.$axios.$get('/api/comments/', { params: { post_id: postId } });
      commit('setComments', { postId, comments });
      return SUCCESS(comments);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },

  async loadNextComments({ commit, state }, postId) {
    try {
      const comments = await this.$axios.$get(state.postCommentsMap[postId].next);
      commit('setNextComments', { postId, comments });
      return SUCCESS(comments);
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
  async addOrRemoveCommentReaction({ commit, state }, { parentId, commentId, action, emoji = 'heart' }) {
    try {
      const updatedComment = await this.$axios.$post(`/api/comments/${commentId}/reactions/`, { action, emoji });
      commit('updateComment', { parentId, commentId, comment: updatedComment });
      return SUCCESS(updatedComment);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async createComment({ commit, dispatch }, { postId, parentId = undefined, body }) {
    try {
      const comment = await this.$axios.$post('/api/comments/', { post_id: postId, parent_id: parentId, body });
      commit('createComment', { postId, parentId, comment });
      // dispatch('updatePostStats'); TODO: refresh stats
      return SUCCESS(comment);
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

  async deleteComment({ commit }, { parentId, commentId }) {
    try {
      await this.$axios.$delete(`/api/comments/${commentId}/`);
      commit('deleteComment', { parentId, commentId });
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
  updatePostStats(state, { postId, stats }) {
    state.postsById[postId].stats = stats;
  },
  deletePost(state, postId) {
    Vue.delete(state.postsById, postId);
  },
  deleteComment(state, { parentId, commentId }) {
    if (!parentId) Vue.delete(state.commentsById, commentId);
    else {
      const idx = state.commentsById[parentId].children.findIndex(comment => comment.id === commentId);
      state.commentsById[parentId].children.splice(idx, 1);
    }
  },
  createComment(state, { postId, parentId, comment }) {
    if (!parentId) {
      Vue.set(state.commentsById, comment.id, comment);
      if (!state.postCommentsMap[postId]) {
        Vue.set(state.postCommentsMap, postId, { previous: null, next: null, commentIds: [] });
      }
      state.postCommentsMap[postId].commentIds.unshift(comment.id);
    } else {
      state.commentsById[parentId].children.push(comment);
    }
  },
  setComments(state, { postId, comments }) {
    const { previous, next, results } = comments;
    results.forEach(comment => {
      Vue.set(state.commentsById, comment.id, comment);
    });
    Vue.set(state.postCommentsMap, postId, { previous, next, commentIds: results.map(c => c.id) });
  },
  setNextComments(state, { postId, comments }) {
    const { previous, next, results } = comments;
    results.forEach(comment => {
      Vue.set(state.commentsById, comment.id, comment);
      state.postCommentsMap[postId].commentIds.push(comment.id);
    });
    Object.assign(state.postCommentsMap[postId], { previous, next });
  },
  updateComment(state, { parentId, commentId, comment }) {
    state.commentsById[commentId] = comment;

    if (!parentId) {
      state.commentsById[commentId] = comment;
    } else {
      const idx = state.commentsById[parentId].children.findIndex(c => c.id === commentId);
      state.commentsById[parentId].children.splice(idx, 1, comment);
    }
  }
};
