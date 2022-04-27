/* eslint no-console: ["warn", { allow: ["error"] }] */

import get from 'lodash/get';
import toast from '~/components/fm/alert/service';

const ERRORED = true;
const NO_ERROR = false;

export const state = () => ({
  donations: null,
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
  // eslint-disable-next-line camelcase
  async fetchReceivedDonations({ dispatch }, { creator_username, search, ordering }) {
    return await dispatch('fetch', {
      url: '/api/donations/',
      payload: { params: { creator_username, search, ordering } },
      mutation: 'setDonations'
    });
  },
  async fetchMoreDonations({ dispatch }, nextUrl) {
    return await dispatch('fetch', { url: nextUrl, mutation: 'setMoreDonations' });
  },
  // eslint-disable-next-line camelcase
  async fetchSentDonations({ dispatch }, { fan_username, search, ordering }) {
    return await dispatch('fetch', {
      url: '/api/donations/',
      payload: { params: { fan_username, search, ordering } },
      mutation: 'setDonations'
    });
  },
  async fetchPayments({ dispatch }, { creatorUsername, fanUsername }) {
    return await dispatch('fetch', {
      url: '/api/payments/',
      payload: { params: { creator_username: creatorUsername, fan_username: fanUsername } },
      mutation: 'setPayments'
    });
  },
  async fetchMorePayments({ dispatch }, nextUrl) {
    return await dispatch('fetch', { url: nextUrl, mutation: 'setMorePayments' });
  }
};

export const mutations = {
  setDonations(state, donations) {
    state.donations = donations;
  },
  setMoreDonations(state, donations) {
    const results = [...state.donations.results, ...donations.results];
    state.donations = { ...donations, results };
  },
  setPayments(state, payments) {
    state.payments = payments;
  },
  setMorePayments(state, payments) {
    const results = [...state.payments.results, ...payments.results];
    state.payments = { ...payments, results };
  }
};
