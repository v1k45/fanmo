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
  isSelfProfile(state, getters, rootState) {
    return !!(
      (get(rootState, 'auth.user.username') && get(state, 'user.username')) &&
      (rootState.auth.user.username === state.user.username)
    );
  },
  currentUserHasActiveSubscription(state, getters, rootState) {
    if (!rootState.auth.loggedIn) return false; // unauthenticated
    const currentMembership = (state.existingMemberships || [])[0];
    if (!currentMembership || !currentMembership.is_active) return false;
    return true;
  },
  currentUserHasActiveAndScheduledSubscription(state, getters, rootState) {
    if (!getters.currentUserHasActiveSubscription) return false;
    if (!rootState.auth.loggedIn) return false; // unauthenticated
    const scheduledSubscription = state.existingMemberships[0].scheduled_subscription;
    if (!scheduledSubscription || scheduledSubscription.status !== 'scheduled_to_activate') return false;
    return true;
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
      return handleGenericError(err, handleAll);
    }
  },

  async updateGeneric({ commit }, { url, payload, method = 'post', handleAll = false }) {
    try {
      const response = await this.$axios[HTTP_METHOD_AXIOS_MAP[method]](url, payload);
      return { error: NO_ERROR, response };
    } catch (err) {
      if (err.response.status >= 500) {
        console.error(err);
        toast.error("Internal server error. It's not you, it's us. Please try again in a minute.");
      } else if (err.response.status >= 400) {
        if (handleAll) toast.error(err.response.data);
        else return { error: ERRORED, response: err.response.data };
      } else if (get(err, 'response.data')) { // shouldn't come here
        console.error(err);
        toast.error(err.response.data);
      } else {
        console.error(err);
        toast.error("We're sorry but an unknown error occurred. If this persists, please contact support.");
      }
      return { error: ERRORED, response: err.response.data };
    }
  },

  // GET
  async fetchProfileUser({ dispatch }, username) {
    return await dispatch('fetch', { url: `/api/users/${username}/`, mutation: 'setProfileUser' });
  },
  async fetchProfileDonations({ dispatch }, username) {
    return await dispatch('fetch', { url: `/api/donations/recent/?creator_username=${username}`, mutation: 'setProfileDonations' });
  },
  async fetchExistingMemberships({ dispatch }, { creatorUsername, fanUsername }) {
    return await dispatch('fetch', { url: '/api/memberships/', payload: { params: { creator_username: creatorUsername, fan_username: fanUsername } }, mutation: 'setExistingMemberships' });
  },

  async fetchProfile({ dispatch, rootState }, username) {
    const errors = await Promise.allSettled([
      dispatch('posts/loadProfilePosts', username, { root: true }),
      dispatch('fetchProfileUser', username),
      dispatch('fetchProfileDonations', username),
      dispatch('fetchExistingMemberships', { creatorUsername: username, fanUsername: get(rootState, 'auth.user.username') })
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
    dispatch('refreshUser', null, { root: true });
    return !!err;
  },

  async updateDonation({ dispatch, state }, { id, payload }) {
    const err = await dispatch('update', {
      method: 'patch',
      url: `/api/donations/${id}/`,
      payload,
      mutation: 'replaceDonation',
      handleAll: true
    });
    if (err) return ERRORED;
    return NO_ERROR;
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
  async createPost({ state, dispatch }, payload) {
    const err = await dispatch('update', { url: '/api/posts/', payload });
    if (err) return err;
    dispatch('posts/loadProfilePosts', state.user.username, { root: true });
    return NO_ERROR;
  },
  async getLinkPreview({ state, dispatch }, link) {
    const { error, response } = await dispatch('updateGeneric', { url: '/api/posts/link_preview/', payload: { link } });
    if (error) return { success: false, data: response };
    return { success: true, data: response };
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
  async createOrGetMembership({ state }, { creator_username, tier_id, email }) {
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

  // eslint-disable-next-line camelcase
  async createDonation({ state, dispatch }, { amount, creator_username, email, message, is_hidden }) {
    let donation;
    try {
      donation = await this.$axios.$post('/api/donations/', { amount, creator_username, email, message, is_hidden });
      return { success: true, data: donation };
    } catch (err) {
      console.error(err.response.data);
      return { success: false, data: err.response.data };
    }
  },

  /*
   To be called with Razorpay's response after a payment is made by the user. Show success dialog as feedback if no error.
  */
  async processPayment({ state, dispatch }, { donationOrSubscription, paymentResponse, supportType }) {
    // eslint-disable-next-line prefer-const
    let { error, response } = await dispatch('updateGeneric', {
      url: '/api/payments/',
      payload: {
        processor: 'razorpay',
        payload: paymentResponse,
        ...(supportType === 'membership'
          ? {
              type: 'subscription',
              subscription_id: donationOrSubscription.id
            }
          : {
              type: 'donation',
              donation_id: donationOrSubscription.id
            })
      }
    });
    if (error) {
      if (typeof response !== 'object') response = {};
      response.non_field_errors = [{
        message: [
          'There was an error while processing the payment.',
          'If money was deducted from your account, it will be automatically refunded in 2 days.',
          'Feel free to contact us if you have any questions.'
        ].join(' ')
      }];
      return { error, response };
    }
    return { error, response };
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
    state.donations = donations.results;
  },
  setExistingMemberships(state, existingMemberships) {
    state.existingMemberships = existingMemberships.results;
  },
  replaceDonation(state, donation) {
    const idxToReplace = (state.donations || []).findIndex(currDonation => currDonation.id === donation.id);
    if (idxToReplace < 0) return;
    state.donations.splice(idxToReplace, 1, donation);
  }
};
