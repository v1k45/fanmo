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
  },

  // MISC
  /*
    On clicking Join/Subscribe on any membership, this should be called. Based on the response, one of the following
    actions should be taken by the calling code based on the returned value.
      Returned value                               Action to take
    - { success: false }                           Show an error.
    - { success: true, data: { ... } }             With `data` having a truthy value (which will hold the membership),
                                                   show the razorpay dialog to initiate the payment. After the payment
                                                   is done, call `processPayment` and show a success dialog as feedback.
    - { success: true, data: null }                With `data` having a falsy value, treat this as payment already being
                                                   successful. Just show the success dialog as feedback.
   */
  // eslint-disable-next-line camelcase
  async createOrGetMembership({ state, dispatch }, { creator_username, tier_id, email }) {
    let membership;
    try {
      const { existingMemberships } = state;
      if (existingMemberships.length) {
        membership = await this.$axios.$patch(
          `/api/memberships/${existingMemberships[0].id}/`,
          { creator_username, tier_id }
        );
      } else {
        membership = await this.$axios.$post('/api/memberships/', { creator_username, tier_id, email });
      }
    } catch (err) {
      console.error(err.response.data);
      return { success: false, data: err.response.data };
    }

    // start payment intent if required
    if (membership.scheduled_subscription.payment.is_required) {
      // TODO: if there is an active subscription
      // let the user know that they are going to pay only Rs. 5 for authorizing the transaction.
      // it will be automatically refunded and the actual subscription amount will be charged
      // when the next subscription cycle starts.
      return { success: true, data: membership.scheduled_subscription };
    }

    return { success: true, data: null };
  },

  /*
   To be called with Razorpay's response after a payment is made by the user. Show success dialog as feedback if no error.
  */
  async processPayment({ state, dispatch }, { subscription, paymentResponse }) {
    let err = await dispatch('update', {
      url: '/api/payments/',
      payload: {
        processor: 'razorpay',
        type: 'subscription',
        subscription_id: subscription.id,
        payload: paymentResponse
      }
    });
    if (err) {
      if (typeof err !== 'object') err = {};
      err.non_field_errors = [{
        message: [
          'There was an error while processing the payment.',
          'If money was deducted from your account, it will be automatically refunded in 2 days.',
          'Feel free to contact us if you have any questions.'
        ].join(' ')
      }];
      return err;
    }
    return NO_ERROR;
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
