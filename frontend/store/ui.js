export const state = () => ({
  showGlobalLoader: false, // <false|string>
  currentPage: null, // pages can set this to show the top nav on phone with title and description
  pages: {
    dashboard: {
      title: 'Dashboard',
      description: 'View recent activities and analytics for your Fanmo page.'
    },
    earnings: {
      title: 'Earnings',
      description: 'View your earnings and stats.'
    },
    posts: {
      title: 'Posts',
      description: 'View and manage your posts.'
    },
    feed: {
      title: 'Feed',
      description: 'Content from all the creators you follow or subscribe to.'
    },
    members: {
      title: 'Members Dashboard',
      description: 'View and manage members, review transaction history and manage membership tiers.'
    },
    memberships: {
      title: 'My Memberships',
      supporterTitle: 'Memberships',
      description: 'View and manage your memberships and review transaction history.'
    },
    receivedDonations: {
      title: 'Tips Dashboard',
      description: 'View and manage tips, tip settings, review transaction history and overall earnings from tips.'
    },
    sentDonations: {
      title: 'My Tips',
      supporterTitle: 'Tips',
      description: 'Search and view your tips.'
    },
    settings: {
      title: 'Settings',
      description: 'Manage your account, notifications and security settings.'
    }
  }
});

export const getters = {
};

export const actions = {
};


export const mutations = {
  setGlobalLoader(state, isVisible) {
    state.showGlobalLoader = isVisible;
  },
  setCurrentPage(state, pageKey) {
    state.currentPage = pageKey;
  }
};
