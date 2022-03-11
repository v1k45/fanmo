export const delay = (ms = 0) => new Promise(resolve => setTimeout(resolve, ms));
export const skipOnboarding = {
  value: (userId) => { return localStorage.getItem(`onboarding:skipped:${userId}`) || false; },
  set: (userId) => localStorage.setItem(`onboarding:skipped:${userId}`, '1'),
  unset: (userId) => localStorage.setItem(`onboarding:skipped:${userId}`, '0')
};
