const currencyFormatter = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' });
const currencyFormatterInteger = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 0 });

export const toCurrency = val => {
  // Number constructor converts null, false, true, empty strings, etc. values to their corresponding numeric values, which we don't want.
  if (!['string', 'number'].includes(typeof val) || val === '') return val;
  return (val % 1 === 0 ? currencyFormatterInteger : currencyFormatter).format(val);
};

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
