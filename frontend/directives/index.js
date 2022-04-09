import intersect from './intersect';
import loading from './loading';

export default (Vue) => {
  Vue.directive('intersect', intersect);
  Vue.directive('loading', loading);
};
