// API https://vuetifyjs.com/en/api/v-intersect/

function inserted(el, binding, vnode) {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) return;

  const modifiers = binding.modifiers || {};
  const value = binding.value;
  const { handler, options } = typeof value === 'object'
    ? value
    : { handler: value, options: {} };
  const observer = new IntersectionObserver((entries = [], observer = IntersectionObserver) => {
    const _observe = el._observe ? el._observe[vnode.context._uid] : null;
    if (!_observe) return; // Just in case, should never fire

    const isIntersecting = entries.some(entry => entry.isIntersecting);

    // If is not quiet or has already been
    // initialized, invoke the user callback
    if (
      handler &&
      (!modifiers.quiet || _observe.init) &&
      (!modifiers.once || isIntersecting || _observe.init)
    ) {
      handler(entries, observer, isIntersecting);
    }

    if (isIntersecting && modifiers.once) unbind(el, binding, vnode);
    else _observe.init = true;
  }, options);

  el._observe = Object(el._observe);
  el._observe[vnode.context._uid] = { init: false, observer };

  observer.observe(el);
}

function unbind(el, binding, vnode) {
  const observe = el._observe ? el._observe[vnode.context._uid] : null;
  if (!observe) return;

  observe.observer.unobserve(el);
  delete el._observe[vnode.context._uid];
}

export default {
  inserted,
  unbind
};
