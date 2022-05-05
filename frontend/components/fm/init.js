import alertService from './alert/service';
import { alertService as dialogAlertService, confirmService } from './dialog/service';
import { toCurrency, toDate, toDatetime } from '~/utils';

export default (context, inject) => {
  inject('toast', alertService);
  inject('alert', dialogAlertService);
  inject('confirm', confirmService);
  inject('currency', toCurrency);
  inject('datetime', toDatetime);
  inject('date', toDate);
};
