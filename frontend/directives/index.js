import intersect from './intersect';
import loading from './loading';
import swipe from './swipe';
import tooltip from './tooltip';

export default (Vue) => {
  Vue.directive('intersect', intersect);
  Vue.directive('loading', loading);
  Vue.directive('swipe', swipe);
  Vue.directive('tooltip', tooltip);
};
