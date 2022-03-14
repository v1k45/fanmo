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

const dialog = ({ dialogType, message, title, html, type }) => {
  const instance = new Dialog();
  const container = document.body;

  Object.assign(instance, { message, title, type, dialogType, html });
  instance.vm = instance.$mount();
  container.appendChild(instance.$el);

  instance.$on('closed', () => {
    destroyInstance(instance);
  });

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

export const confirmService = (message, title, options = {}) => dialog({ message, title, ...options, dialogType: 'confirm' });
confirmService.info = (message, title, options = {}) => dialog({ message, title, ...options, type: 'info', dialogType: 'confirm' });
confirmService.warning = (message, title, options = {}) => dialog({ message, title, ...options, type: 'warning', dialogType: 'confirm' });
confirmService.error = (message, title, options = {}) => dialog({ message, title, ...options, type: 'error', dialogType: 'confirm' });
confirmService.success = (message, title, options = {}) => dialog({ message, title, ...options, type: 'success', dialogType: 'confirm' });
