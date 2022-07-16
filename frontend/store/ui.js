export const state = () => ({
  showGlobalLoader: false // <false|string>
});

export const getters = {
};

export const actions = {
};


export const mutations = {
  setGlobalLoader(state, isVisible) {
    state.showGlobalLoader = isVisible;
  }
};
