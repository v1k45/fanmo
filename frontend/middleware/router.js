/* eslint-disable camelcase */
import get from 'lodash/get';
import { skipOnboarding } from '~/utils';

const allowedRoutes = {
  'onboarding-role': [],
  'onboarding-verify': ['onboarding-role'],
  'onboarding-profile-info': ['onboarding-role'],
  'onboarding-payment-info': ['onboarding-role', 'onboarding-profile-info']
};

export default function(ctx) {
  const { $auth, route, store, next } = ctx;

  store.commit('ui/setCurrentPage', null);

  if (!$auth.loggedIn || !$auth.user) return;

  // if authentication is triggered by express checkout, let the parent tab know.
  if (window.opener) {
    try {
      // notify parent tab and close window if the tab was triggered internally.
      if (window.opener.location.origin === location.origin) {
        window.opener.postMessage('refresh_login', {});
        window.close();
      }
    } catch (e) {
      // this tab was triggered by a cross-origin opener of a website run by retards who don't know how to use target="_blank" on their website.
      window.opener.postMessage('fuck_you_madarchod', {});
    }
  }

  const user = $auth.user;
  const nextIfNeeded = ({ name }) => {
    if (allowedRoutes[name].includes(route.name)) return;
    if (route.name !== name) next({ name });
  };
  const { email_verification, type_selection, introduction, payment_setup } = user.onboarding.checklist;
  if (
    get(user, 'onboarding.status') === 'in_progress' &&
    !skipOnboarding.value(user.username)
  ) {
    if (!type_selection) nextIfNeeded({ name: 'onboarding-role' });
    else if (!email_verification) nextIfNeeded({ name: 'onboarding-verify' }); // can be skipped by supporters
    else if (user.is_creator) {
      if (!introduction) nextIfNeeded({ name: 'onboarding-profile-info' });
      else if (!payment_setup) nextIfNeeded({ name: 'onboarding-payment-info' }); // can be skipped by creators
    }
  }
}
