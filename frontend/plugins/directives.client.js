import Vue from 'vue';
import Loader from '~/components/misc/loading.vue';

const Component = Vue.extend(Loader);

const destroyInstance = instance => {
  const el = instance.$el;
  el.parentNode.removeChild(el);
  instance.$destroy();
};

const bindUpdateHandler = (el, binding) => {
  // when updating, destroy the previous instance
  if (el.$loaderInstance || (!binding.value && el.$loaderInstance)) destroyInstance(el.$loaderInstance);
  if (!binding.value) return;

  // create instance and pass props
  const instance = new Component();
  if (typeof binding.value === 'string') instance.text = binding.value;

  // mount
  instance.vm = instance.$mount();
  el.appendChild(instance.$el);

  // store reference to destroy in unbind/update
  el.$loaderInstance = instance;
};

Vue.directive('loading', {
  bind: bindUpdateHandler,
  update: bindUpdateHandler,
  unbind: el => {
    if (el.$loaderInstance) destroyInstance(el.$loaderInstance);
  }
});
