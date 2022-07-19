import intersect from './intersect';
import loading from './loading';
import tooltip from './tooltip';

export default (Vue) => {
  Vue.directive('intersect', intersect);
  Vue.directive('loading', loading);
  Vue.directive('tooltip', tooltip);
};
