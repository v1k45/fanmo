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
  const { $auth, route, next } = ctx;
  if (!$auth.loggedIn || !$auth.user) return;
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
