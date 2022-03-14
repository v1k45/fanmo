import Vue from 'vue';
import component from './service-alert.vue';

const Alert = Vue.extend(component);

const destroyInstance = (instance) => {
  const el = instance.$el;
  el.parentNode.removeChild(el);
  const container = getAlertContainer();
  if (!container.children.length) container.parentNode.removeChild(container);
  instance.$destroy();
};

const getAlertContainer = () => {
  let container = document.querySelector('.fm-alert__container');
  if (!container) {
    container = document.createElement('div');
    container.classList.add('fm-alert__container');
    document.body.appendChild(container);
  }
  return container;
};

const alert = ({ message, title, html, type = 'info', timeout = 5000 }) => {
  const instance = new Alert();
  const container = getAlertContainer();

  Object.assign(instance, { message, title, type, timeout, html });
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

const alertService = (message, title, options = {}) => alert({ message, title, ...options });
alertService.info = (message, title, options = {}) => alert({ message, title, ...options, type: 'info' });
alertService.warning = (message, title, options = {}) => alert({ message, title, ...options, type: 'warning' });
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
  alert({ message, title, html, ...options, type: 'error' });
};
alertService.success = (message, title, options = {}) => alert({ message, title, ...options, type: 'success' });

export default alertService;
