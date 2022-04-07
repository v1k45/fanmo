/* eslint no-console: ["warn", { allow: ["error"] }] */
import get from 'lodash/get';
import toast from '~/components/fm/alert/service';

const ERRORED = data => ({ error: true, data });
const NO_ERROR = data => ({ error: false, data });

export const state = () => ({});

export const mutations = {};

export const getters = {};

export const actions = {
  async fetch({ commit }, { url, payload, mutation }) {
    try {
      const response = await this.$axios.$get(url, payload);
      if (mutation) commit(mutation, response);
      return NO_ERROR(response);
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
      return ERRORED(err);
    }
  },
  async refreshUser({ dispatch }) {
    const { error, data } = await dispatch('fetch', { url: '/api/me/', mutation: 'setProfileUser' });
    if (error) return;
    this.$auth.setUser(data);
  }
};
