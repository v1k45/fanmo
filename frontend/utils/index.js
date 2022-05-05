import dayjs from 'dayjs';

const currencyFormatter = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' });
const currencyFormatterInteger = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 0 });

export const toCurrency = val => {
  // Number constructor converts null, false, true, empty strings, etc. values to their corresponding numeric values, which we don't want.
  if (!['string', 'number'].includes(typeof val) || val === '') return val;
  return (val % 1 === 0 ? currencyFormatterInteger : currencyFormatter).format(val);
};

export const toDatetime = val => {
  if (!['string', 'number'].includes(typeof val) || val === '') return val;
  return dayjs(val).format('D MMM, YYYY hh:mma');
};
export const toDate = val => {
  if (!['string', 'number'].includes(typeof val) || val === '') return val;
  return dayjs(val).format('D MMM, YYYY');
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

/**
* We use shorter names to reduce the final bundle size
*
* Properties:
* @url = url
* @text = title
* @hashtags = hashtags
*/
const socialSharingSchema = Object.freeze({
  email: 'mailto:?subject=@text&body=@url',
  facebook: 'https://www.facebook.com/sharer/sharer.php?u=@url&title=@text&hashtag=@hashtags',
  reddit: 'https://www.reddit.com/submit?url=@url&title=@text',
  telegram: 'https://t.me/share/url?url=@url&text=@text',
  twitter: 'https://twitter.com/intent/tweet?text=@text&url=@url&hashtags=@hashtags',
  whatsapp: 'https://api.whatsapp.com/send?text=@text%0D%0A@url'
});

export const getSocialLink = (social, { url, text }) => {
  let template = socialSharingSchema[social];
  if (!template) throw new Error('Unsupported social');
  template = template.replace('@url', encodeURIComponent(url));
  template = template.replace('@text', encodeURIComponent(text));
  template = template.replace('@hashtags', encodeURIComponent('fanmo'));
  return template;
};


/**
 * Copies the provided text to the clipboard.
 * @param {string} text - text to copy to the clipboard
 * @returns {Promise} A promise that gets resolved or rejected based on whether the text was successfully copied to the clipboard
 */
export const copy = (() => {
  // modified from here: https://stackoverflow.com/a/30810322

  const fallbackCopyTextToClipboard = text => {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();

    let success = false;
    try {
      success = document.execCommand('copy');
    } catch (err) {
      success = false;
    }

    document.body.removeChild(textarea);
    return success;
  };

  const copyTextToClipboard = text => {
    if (!navigator.clipboard) {
      const success = fallbackCopyTextToClipboard(text);
      // eslint-disable-next-line prefer-promise-reject-errors
      return success ? Promise.resolve() : Promise.reject();
    }
    return navigator.clipboard.writeText(text);
  };

  return copyTextToClipboard;
})();

export const STATUS_TEXT_MAP = {
  created: 'Created',
  authenticated: 'Authenticated',
  active: 'Active', // charged successfully
  scheduled_to_activate: 'Scheduled to activate', // will be activated in next cycle
  pending: 'Pending', // renewing at end of cycle
  halted: 'Halted',
  scheduled_to_cancel: 'Scheduled to cancel', // used when updating current subscription
  cancelled: 'Cancelled',
  paused: 'Paused',
  expired: 'Expired',
  completed: 'Completed'
};
