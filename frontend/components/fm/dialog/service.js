import Vue from 'vue';
import component from './service-dialog.vue';

const Dialog = Vue.extend(component);

const destroyInstance = (instance) => {
  const el = instance.$el;
  el.parentNode.removeChild(el);
  const container = document.body;
  if (!container.children.length) container.parentNode.removeChild(container);
  instance.$destroy();
};

const dialog = ({ dialogType, message, title, html, type, returnPromise = false }) => {
  const instance = new Dialog();
  const container = document.body;

  Object.assign(instance, { message, title, type, dialogType, html });
  instance.vm = instance.$mount();
  container.appendChild(instance.$el);

  instance.$on('closed', () => {
    destroyInstance(instance);
  });

  if (returnPromise) {
    const promise = new Promise((resolve, reject) => {
      instance.$on('ok', () => resolve());
      // eslint-disable-next-line prefer-promise-reject-errors
      instance.$on('cancel', () => reject());
      // eslint-disable-next-line prefer-promise-reject-errors
      instance.$on('closed', () => reject());
    });
    return promise;
  };

  return {
    close: () => {
      instance.isVisible = false;
    }
  };
};

export const alertService = (message, title, options = {}) => dialog({ message, title, ...options, dialogType: 'alert' });
alertService.info = (message, title, options = {}) => dialog({ message, title, ...options, type: 'info', dialogType: 'alert' });
alertService.warning = (message, title, options = {}) => dialog({ message, title, ...options, type: 'warning', dialogType: 'alert' });
alertService.error = (message, title, options = {}) => {
  let html = false;
  if (typeof message === 'object') {
    let errors = [];
    if (message.non_field_errors) errors = message.non_field_errors;
    else if (message.detail) errors = [message.detail];
    if (errors.length) {
      message = errors.map(err => err.message).join('<br>');
      html = true;
    }
  }
  return dialog({ message, title, html, ...options, type: 'error', dialogType: 'alert' });
};
alertService.success = (message, title, options = {}) => dialog({ message, title, ...options, type: 'success', dialogType: 'alert' });

export const confirmService = (message, title, options = {}) => dialog({ message, title, ...options, returnPromise: true, dialogType: 'confirm' });
confirmService.info = (message, title, options = {}) => dialog({ message, title, ...options, type: 'info', returnPromise: true, dialogType: 'confirm' });
confirmService.warning = (message, title, options = {}) => dialog({ message, title, ...options, type: 'warning', returnPromise: true, dialogType: 'confirm' });
confirmService.error = (message, title, options = {}) => dialog({ message, title, ...options, type: 'error', returnPromise: true, dialogType: 'confirm' });
confirmService.success = (message, title, options = {}) => dialog({ message, title, ...options, type: 'success', returnPromise: true, dialogType: 'confirm' });
