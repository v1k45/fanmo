import alertService from './alert/service';
import { alertService as dialogAlertService, confirmService } from './dialog/service';
import { toCurrency } from '~/utils';

export default (context, inject) => {
  inject('toast', alertService);
  inject('alert', dialogAlertService);
  inject('confirm', confirmService);
  inject('currency', toCurrency);
};
