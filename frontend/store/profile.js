/* eslint no-console: ["warn", { allow: ["error"] }] */

import get from 'lodash/get';
import toast from '~/components/fm/alert/service';

const ERRORED = true;
const NO_ERROR = false;

const HTTP_METHOD_AXIOS_MAP = {
  GET: '$get',
  POST: '$post',
  PATCH: '$patch',
  PUT: '$post',
  DELETE: '$delete',
  get: '$get',
  post: '$post',
  patch: '$patch',
  put: '$post',
  delete: '$delete'
};

export const state = () => ({
  user: null,
  posts: null,
  donations: null,
  existingMemberships: null
});

export const getters = {
  isSelfProfile(state, getters, rootState) {
    return !!(
      (get(rootState, 'auth.user.username') && get(state, 'user.username')) &&
      (rootState.auth.user.username === state.user.username)
    );
  }
};

export const actions = {
  async fetch({ commit }, { url, payload, mutation }) {
    try {
      const response = await this.$axios.$get(url, payload);
      if (mutation) commit(mutation, response);
      return NO_ERROR;
    } catch (err) {
      if (err.response.status >= 500) {
        console.error(err);
        toast.error("Internal server error. It's not you, it's us. Please try again in a minute.");
      } else if (err.response.status >= 400) {
        toast.error(err.response.data);
      } else if (get(err, 'response.data')) { // shouldn't come here
        console.error(err);
        toast.error(err.response.data);
      } else {
        console.error(err);
        toast.error("We're sorry but an unknown error occurred. If this persists, please contact support.");
      }
      return ERRORED;
    }
  },

  async update({ commit }, { url, payload, method = 'post', mutation, handleAll = false }) {
    try {
      const response = await this.$axios[HTTP_METHOD_AXIOS_MAP[method]](url, payload);
      if (mutation) commit(mutation, response);
      return NO_ERROR;
    } catch (err) {
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
    }
  },

  // GET
  async fetchProfileUser({ dispatch }, username) {
    return await dispatch('fetch', { url: `/api/users/${username}/`, mutation: 'setProfileUser' });
  },
  async fetchProfilePosts({ dispatch }, username) {
    return await dispatch('fetch', { url: `/api/posts/?username=${username}`, mutation: 'setProfilePosts' });
  },
  async fetchProfileDonations({ dispatch }, username) {
    return await dispatch('fetch', { url: `/api/donations/?username=${username}`, mutation: 'setProfileDonations' });
  },
  async fetchExistingMemberships({ dispatch }, username) {
    return await dispatch('fetch', { url: `/api/memberships/?username=${username}`, mutation: 'setExistingMemberships' });
  },

  async fetchProfile({ dispatch }, username) {
    const errors = await Promise.allSettled([
      dispatch('fetchProfileUser', username),
      dispatch('fetchProfilePosts', username),
      dispatch('fetchProfileDonations', username),
      dispatch('fetchExistingMemberships', username)
    ]);
    return errors.some(err => !!err) ? ERRORED : NO_ERROR;
  },

  // PATCH
  async updateUser({ dispatch, state }, { payload, handleAll = false }) {
    let err = await dispatch('update', {
      method: 'patch',
      url: '/api/me/',
      payload,
      mutation: 'setProfileUser',
      handleAll
    });
    if (err) return ERRORED;
    err = await dispatch('fetchProfileUser', state.user.username);
    return !!err;
  },

  // POST
  async follow({ state, dispatch }) {
    let err = await dispatch('update', {
      url: `/api/users/${state.user.username}/follow/`,
      handleAll: true
    });
    if (err) return ERRORED;
    err = await dispatch('fetchProfileUser', state.user.username);
    return !!err;
  },
  async unfollow({ state, dispatch }) {
    let err = await dispatch('update', {
      url: `/api/users/${state.user.username}/unfollow/`,
      handleAll: true
    });
    if (err) return ERRORED;
    err = await dispatch('fetchProfileUser', state.user.username);
    return !!err;
  }
};


export const mutations = {
  setProfileUser(state, user) {
    state.user = user;
  },
  setProfilePosts(state, posts) {
    state.posts = posts;
  },
  setProfileDonations(state, donations) {
    state.donations = donations;
  },
  setExistingMemberships(state, existingMemberships) {
    state.existingMemberships = existingMemberships.results;
  }
};
