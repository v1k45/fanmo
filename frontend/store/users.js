import Vue from 'vue';
import { handleGenericError } from '~/utils';

const SUCCESS = (data) => ({ success: true, data });
const ERROR = (data) => ({ success: false, data });

export const state = () => ({
  usersById: {}, // { [userId]: { ...user } }
  raw: {
    following: null // { previous, next, count, userIds }
  }
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
  }
};


export const mutations = {
  setFollowingUsers(state, { users }) {
    const { previous, next, count, results } = users;
    results.forEach(user => {
      Vue.set(state.usersById, user.id, user);
    });
    state.raw.following = {
      previous,
      next,
      count,
      userIds: results.map(user => user.id)
    };
  },
  setNextFollowingUsers(state, { users }) {
    const { previous, next, count, results } = users;
    results.forEach(user => {
      Vue.set(state.usersById, user.id, user);
      state.raw.following.userIds.push(user.id);
    });
    Object.assign(state.raw.following, { previous, next, count });
  }
};
