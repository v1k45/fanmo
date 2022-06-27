/* eslint no-console: ["warn", { allow: ["error"] }] */
import dayjs from 'dayjs';
import get from 'lodash/get';
import toast from '~/components/fm/alert/service';

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

/**
 * @param {*} err - axios error to handle. if it's not an axios error, this will result in another error
 * @param {*} handleAll - whether 400s should be handled by the function too.
 * @returns {*|Boolean} - error object from server or `true` otherwise to convey error
 */
export const handleGenericError = (err, handleAll = false) => {
  if (process.env.NODE_ENV !== 'production') console.error(err);
  if (err.response.status >= 500) {
    console.error(err);
    toast.error("Internal server error. It's not you, it's us. Please try again in a minute.");
  } else if (err.response.status >= 400) {
    if (handleAll) toast.error(err.response.data);
    else return err.response.data;
  } else if (get(err, 'response.data')) { // shouldn't come here
    console.error(err);
    toast.error(err.response.data);
  } else {
    console.error(err);
    toast.error("We're sorry but an unknown error occurred. If this persists, please contact support.");
  }
  return true;
};

export const getBase64FromFile = async (file) => {
  const reader = new FileReader();
  reader.readAsDataURL(file);
  const fileReaderResult = await new Promise(resolve => {
    reader.onload = loadEvent => resolve(loadEvent);
  });
  return fileReaderResult.target.result;
};

/**
 * Masks everything except the last 4 character of the passed string. If the string is <=4 characters,
 * half (ceiling) its characters are masked instead.
 * @param {string} str - string to mask
 * @param {string} maskWith - masking character(s)
 * @returns {string} masked string
 */
export const maskString = (str, maskWith = 'X') => {
  if (typeof str !== 'string') return str;
  const charCountToMask = Math.max(Math.ceil(str.length / 2), str.length - 4);
  return maskWith.repeat(charCountToMask) + str.slice(charCountToMask);
};
