export const delay = (ms = 0) => new Promise(resolve => setTimeout(resolve, ms));
export const skipOnboarding = {
  value: (userId) => { return localStorage.getItem(`onboarding:skipped:${userId}`) || false; },
  set: (userId) => localStorage.setItem(`onboarding:skipped:${userId}`, '1'),
  unset: (userId) => localStorage.setItem(`onboarding:skipped:${userId}`, '0')
};
export const loadScript = url => {
  const script = document.createElement('script');
  script.src = url;
  script.async = true;
  document.body.appendChild(script);

  return new Promise((resolve, reject) => {
    script.onerror = reject;
    script.onload = resolve;
  });
};

export const loadRazorpay = () => {
  if (window.Razorpay) return Promise.resolve();
  return loadScript('https://checkout.razorpay.com/v1/checkout.js');
};
