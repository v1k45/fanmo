/* eslint no-console: ["warn", { allow: ["error"] }] */
import Vue from 'vue';
import { handleGenericError } from '~/utils';

const SUCCESS = (data) => ({ success: true, data });
const ERROR = (data) => ({ success: false, data });

export const state = () => ({
  postsById: {}, // { [postId]: { ...post } }
  commentsById: {}, // { [commentId]: comment }
  postCommentsMap: {}, // { [postId]: { previous, next, count, commentIds: [] } }
  donationCommentsMap: {} // { [postId]: { previous, next, count, commentIds: [] } }
});

export const getters = {
};

export const actions = {
  async loadComments({ commit, state }, { postId, donationId }) {
    try {
      const comments = await this.$axios.$get('/api/comments/', { params: { post_id: postId, donation_id: donationId } });
      commit('setComments', { postId, donationId, comments });
      return SUCCESS(comments);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },

  async loadNextComments({ commit, state }, { postId, donationId }) {
    try {
      const nextUrl = (postId ? state.postCommentsMap[postId] : state.donationCommentsMap[donationId]).next;
      const comments = await this.$axios.$get(nextUrl);
      commit('setNextComments', { postId, donationId, comments });
      return SUCCESS(comments);
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
  async createComment({ commit, dispatch }, { postId, donationId, parentId = undefined, body, pushToTop }) {
    try {
      const comment = await this.$axios.$post('/api/comments/', { post_id: postId, donation_id: donationId, parent_id: parentId, body });
      commit('createComment', { postId, donationId, parentId, comment, pushToTop });
      return SUCCESS(comment);
    } catch (err) {
      handleGenericError(err);
      return ERROR(err.response.data);
    }
  },

  // delete
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
  deleteComment(state, { parentId, commentId }) {
    if (!parentId) Vue.delete(state.commentsById, commentId);
    else {
      const idx = state.commentsById[parentId].children.findIndex(comment => comment.id === commentId);
      state.commentsById[parentId].children.splice(idx, 1);
    }
  },
  createComment(state, { postId, donationId, parentId, comment, pushToTop }) {
    if (!parentId) {
      Vue.set(state.commentsById, comment.id, comment);
      // TODO: remove duplication
      if (postId) {
        if (!state.postCommentsMap[postId]) {
          Vue.set(state.postCommentsMap, postId, { previous: null, next: null, count: 0, commentIds: [] });
        }
        state.postCommentsMap[postId].commentIds[pushToTop ? 'unshift' : 'push'](comment.id);
      } else if (donationId) {
        if (!state.donationCommentsMap[donationId]) {
          Vue.set(state.donationCommentsMap, donationId, { previous: null, next: null, count: 0, commentIds: [] });
        }
        state.donationCommentsMap[donationId].commentIds[pushToTop ? 'unshift' : 'push'](comment.id);
      }
    } else {
      state.commentsById[parentId].children.push(comment);
    }
  },
  setComments(state, { postId, donationId, comments }) {
    const { previous, next, count, results } = comments;
    results.forEach(comment => {
      Vue.set(state.commentsById, comment.id, comment);
    });
    if (postId) {
      Vue.set(state.postCommentsMap, postId, { previous, next, count, commentIds: results.map(c => c.id) });
    } else if (donationId) {
      Vue.set(state.donationCommentsMap, donationId, { previous, next, count, commentIds: results.map(c => c.id) });
    }
  },
  setNextComments(state, { postId, donationId, comments }) {
    const { previous, next, count, results } = comments;
    results.forEach(comment => {
      Vue.set(state.commentsById, comment.id, comment);
      if (postId) {
        state.postCommentsMap[postId].commentIds.push(comment.id);
      } else if (donationId) {
        state.donationCommentsMap[donationId].commentIds.push(comment.id);
      }
    });
    if (postId) {
      Object.assign(state.postCommentsMap[postId], { previous, next, count });
    } else if (donationId) {
      Object.assign(state.donationCommentsMap[donationId], { previous, next, count });
    }
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
