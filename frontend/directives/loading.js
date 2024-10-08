import Vue from 'vue';
import Loader from '~/components/misc/loading.vue';

const Component = Vue.extend(Loader);

const destroyInstance = instance => {
  const el = instance.$el;
  if (!el || !el.parentNode) return;
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
  if (binding.modifiers.fullscreen) document.body.appendChild(instance.$el);
  else el.appendChild(instance.$el);

  // store reference to destroy in unbind/update
  el.$loaderInstance = instance;
};

export default {
  bind: bindUpdateHandler,
  update: bindUpdateHandler,
  unbind: el => {
    if (el.$loaderInstance) destroyInstance(el.$loaderInstance);
  }
};
