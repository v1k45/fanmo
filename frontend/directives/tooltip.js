import Vue from 'vue';
import component from '~/components/fm/tooltip/index.vue';

const Tooltip = Vue.extend(component);
const validPlacements = ['top', 'right', 'bottom', 'left'].reduce((arr, position) => {
  arr.push(`${position}-start`, position, `${position}-end`);
  return arr;
}, []);

const getTooltipContainer = () => {
  let el = document.querySelector('#tooltip-container');
  if (!el) {
    el = document.createElement('DIV');
    el.id = 'tooltip-container';
    document.body.appendChild(el);
  }
  return el;
};

const destroyInstance = instance => {
  const el = instance.$el;
  el.parentNode.removeChild(el);
  instance.$destroy();

  const container = getTooltipContainer();
  if (container.getElementsByTagName('*').length === 0) container.parentNode.removeChild(container);
};

const bindUpdateHandler = (el, binding) => {
  // when updating, destroy the previous instance
  if (el.$tooltipInstance) destroyInstance(el.$tooltipInstance);

  // prepare props
  const props = typeof binding.value === 'object'
    ? { reference: el, ...binding.value }
    : { reference: el, content: binding.value };
  const placement = validPlacements.find(placement => binding.arg === placement);

  if (placement && !Object.prototype.hasOwnProperty.call(props, 'placement')) props.placement = placement;

  // create instance and pass props
  const instance = new Tooltip();
  Object.assign(instance, props);

  // mount
  instance.vm = instance.$mount();
  getTooltipContainer().appendChild(instance.$el);

  // store reference to destroy in unbind/update
  el.$tooltipInstance = instance;
};

export default {
  bind: bindUpdateHandler,
  update: bindUpdateHandler,
  unbind: el => {
    if (el.$tooltipInstance) destroyInstance(el.$tooltipInstance);
  }
};
