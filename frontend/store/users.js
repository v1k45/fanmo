import Vue from 'vue';
import { handleGenericError } from '~/utils';

const SUCCESS = (data) => ({ success: true, data });
const ERROR = (data) => ({ success: false, data });

export const state = () => ({
  usersById: {}, // { [userId]: { ...user } }
  raw: {
    following: null // { previous, next, count, userIds }
  },
  accounts: null, // authenticated user's bank accounts
  analytics: null, // authenticated user's analytics
  activities: null // authenticated user's recent activities
});

export const getters = {
  following(state) {
    if (!state.raw.following) return { previous: null, next: null, results: [] };
    return {
      ...state.raw.following,
      results: (state.raw.following.userIds || []).map(userId => state.usersById[userId]).filter(user => !!user)
    };
  }
};

export const actions = {
  async loadFollowingUsers({ commit }) {
    try {
      const users = await this.$axios.$get('/api/users/?is_following=true&page_size=100');
      commit('setFollowingUsers', { users });
      return SUCCESS(users);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadNextFollowingUsers({ commit, state }) {
    try {
      const users = await this.$axios.$get(state.raw.following.next);
      commit('setNextFollowingUsers', { users });
      return SUCCESS(users);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadAccounts({ commit, state }) {
    try {
      const accounts = await this.$axios.$get('/api/accounts/');
      commit('setAccounts', { accounts });
      return SUCCESS(accounts);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadAnalytics({ commit }, period) {
    try {
      const analytics = await this.$axios.$get('/api/stats/', {
        params: {
          period
        }
      });
      commit('setAnalytics', { analytics });
      return SUCCESS(analytics);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadActivities({ commit }) {
    try {
      const activities = await this.$axios.$get('/api/activities/');
      commit('setActivities', { activities });
      return SUCCESS(activities);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async loadNextActivities({ commit, state }) {
    try {
      const activities = await this.$axios.$get(state.activities.next);
      commit('setNextActivities', { activities });
      return SUCCESS(activities);
    } catch (err) {
      handleGenericError(err, true);
      return ERROR(err.response.data);
    }
  },
  async updateSelfUser({ dispatch, state }, payload) {
    try {
      const user = await this.$axios.$patch('/api/me/', payload);
      await dispatch('refreshUser', null, { root: true });
      return SUCCESS(user);
    } catch (err) {
      handleGenericError(err);
      return ERROR(err.response.data);
    }
  },
  async updatePassword({ dispatch }, payload) {
    try {
      const user = await this.$axios.$post('/api/auth/password/change/', payload);
      await dispatch('refreshUser', null, { root: true });
      return SUCCESS(user);
    } catch (err) {
      handleGenericError(err);
      return ERROR(err.response.data);
    }
  }
};


export const mutations = {
  setFollowingUsers(state, { users }) {
    const { previous, next, count, results } = users;
    results.forEach(user => {
      Vue.set(state.usersById, user.username, user);
    });
    state.raw.following = {
      previous,
      next,
      count,
      userIds: results.map(user => user.username)
    };
  },
  setNextFollowingUsers(state, { users }) {
    const { previous, next, count, results } = users;
    results.forEach(user => {
      Vue.set(state.usersById, user.username, user);
      state.raw.following.userIds.push(user.username);
    });
    Object.assign(state.raw.following, { previous, next, count });
  },
  setAccounts(state, { accounts }) {
    state.accounts = accounts;
  },
  setAnalytics(state, { analytics }) {
    state.analytics = analytics;
  },
  setActivities(state, { activities }) {
    state.activities = activities;
  },
  setNextActivities(state, { activities }) {
    state.activities.results.push(...activities.results);
    Object.assign(state.activities, { previous: activities.previous, next: activities.next, count: activities.count });
  }
};
