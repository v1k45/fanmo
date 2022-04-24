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
  memberships: null,
  members: null,
  payments: null
});

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
  // eslint-disable-next-line camelcase
  async fetchMembers({ dispatch }, { creator_username, is_active, search, ordering }) {
    return await dispatch('fetch', {
      url: '/api/memberships/',
      payload: { params: { creator_username, is_active, search, ordering } },
      mutation: 'setMembers'
    });
  },
  async fetchMoreMembers({ dispatch }, nextUrl) {
    return await dispatch('fetch', { url: nextUrl, mutation: 'setMoreMembers' });
  },
  // eslint-disable-next-line camelcase
  async fetchMemberships({ dispatch }, { fan_username, is_active, search, ordering }) {
    return await dispatch('fetch', {
      url: '/api/memberships/',
      payload: { params: { fan_username, is_active, search, ordering } },
      mutation: 'setMemberships'
    });
  },
  async fetchMoreMemberships({ dispatch }, nextUrl) {
    return await dispatch('fetch', { url: nextUrl, mutation: 'setMoreMemberships' });
  },
  async cancelMembership({ dispatch }, membershipId) {
    return await dispatch('update', {
      url: `/api/memberships/${membershipId}/cancel/`,
      mutation: 'cancelMembership',
      handleAll: true
    });
  },
  async fetchPayments({ dispatch }, membershipId) {
    return await dispatch('fetch', {
      url: `/api/payments/?membership_id=${membershipId}`,
      mutation: 'setPayments'
    });
  },
  async fetchMorePayments({ dispatch }, nextUrl) {
    return await dispatch('fetch', { url: nextUrl, mutation: 'setMorePayments' });
  }
};

export const mutations = {
  setMembers(state, members) {
    state.members = members;
  },
  setMoreMembers(state, members) {
    const results = [...state.members.results, ...members.results];
    state.members = { ...members, results };
  },
  setMemberships(state, memberships) {
    state.memberships = memberships;
  },
  setMoreMemberships(state, memberships) {
    const results = [...state.memberships.results, ...memberships.results];
    state.memberships = { ...memberships, results };
  },
  cancelMembership(state, membership) {
    const results = [...state.members.results];
    results.splice(results.findIndex(m => m.id === membership.id), 1, membership);
    state.members.results = results;
  },
  setPayments(state, payments) {
    state.payments = payments;
  },
  setMorePayments(state, payments) {
    const results = [...state.payments.results, ...payments.results];
    state.payments = { ...payments, results };
  }
};
