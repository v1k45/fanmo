import Vue from 'vue';
import alertService from './alert/service';
import { alertService as dialogAlertService, confirmService } from './dialog/service';

import Alert from './alert';
import Avatar from './avatar';
import Button from './button';
import Card from './card';
import Carousel from './carousel';
import Dialog from './dialog';
import Dropdown from './dropdown';
import DropdownDivider from './dropdown/divider';
import DropdownItem from './dropdown/item';
import Editor from './editor';
import Form from './form';
import Input from './input';
import Lazy from './lazy';
import MarkdownStyled from './markdown/styled';
import Marquee from './marquee';
import Popper from './popper';
import ReadMore from './read-more';
import ReadMoreHeight from './read-more/height';
import Table from './table';
import Tabs from './tabs';
import TabsPane from './tabs/pane';
import Timeline from './timeline';
import TimelineItem from './timeline/item';
import Tooltip from './tooltip';
import Wizard from './wizard';
import WizardStep from './wizard/step';


import { toCurrency, toDate, toDatetime } from '~/utils';

export default (context, inject, ...args) => {
  Vue.component('FmAlert', Alert);
  Vue.component('FmAvatar', Avatar);
  Vue.component('FmButton', Button);
  Vue.component('FmCard', Card);
  Vue.component('FmCarousel', Carousel);
  Vue.component('FmDialog', Dialog);
  Vue.component('FmDropdown', Dropdown);
  Vue.component('FmDropdownDivider', DropdownDivider);
  Vue.component('FmDropdownItem', DropdownItem);
  Vue.component('FmEditor', Editor);
  Vue.component('FmForm', Form);
  Vue.component('FmInput', Input);
  Vue.component('FmLazy', Lazy);
  Vue.component('FmMarkdownStyled', MarkdownStyled);
  Vue.component('FmMarquee', Marquee);
  Vue.component('FmPopper', Popper);
  Vue.component('FmReadMore', ReadMore);
  Vue.component('FmReadMoreHeight', ReadMoreHeight);
  Vue.component('FmTable', Table);
  Vue.component('FmTabs', Tabs);
  Vue.component('FmTabsPane', TabsPane);
  Vue.component('FmTimeline', Timeline);
  Vue.component('FmTimelineItem', TimelineItem);
  Vue.component('FmTooltip', Tooltip);
  Vue.component('FmWizard', Wizard);
  Vue.component('FmWizardStep', WizardStep);

  inject('toast', alertService);
  inject('alert', dialogAlertService);
  inject('confirm', confirmService);
  inject('currency', toCurrency);
  inject('datetime', toDatetime);
  inject('date', toDate);
};
