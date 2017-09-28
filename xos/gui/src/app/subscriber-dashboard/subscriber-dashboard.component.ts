/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import * as _ from 'lodash';
import './subscriber-dashboard.scss';

import {IRCordSubscriber, IRCordSubscriberDevice} from '../interfaces/rcord-subscriber.interface';

class RcordSubscriberDashboardCtrl {

  static $inject = [
    'toastr',
    'XosModelStore',
    'XosModeldefsCache'
  ];

  public levelOptions = [];
  public subscribers: IRCordSubscriber[] = [];
  public statusFieldOptions = [];
  public slider = {
    floor: 0,
    ceil: 1000000000,
    translate: (value) => {
      return `${Math.floor(value / 1000000)} MB`;
    }
  };
  public selectedSubscriber: IRCordSubscriber;

  private subscriberDef;

  constructor (
    private toastr: any,
    private XosModelStore: any,
    private XosModeldefsCache: any
  ) {

  }

  $onInit() {
    this.XosModelStore.query('CordSubscriberRoot', '/rcord/cordsubscriberroots')
      .subscribe(
        res => {
          this.subscribers = this.parseSubscribers(res);
        }
      );

    this.levelOptions = [
      `G`,
      `PG`,
      `PG_13`,
      `R`,
      `X`
    ];

    this.subscriberDef = this.XosModeldefsCache.get('CordSubscriberRoot');
    this.statusFieldOptions = _.find(this.subscriberDef.fields, {name: 'status'}).options;
  }

  public addDevice(subscriber: IRCordSubscriber) {
    if (angular.isUndefined(subscriber.service_specific_attribute.devices)) {
      subscriber.service_specific_attribute.devices = [];
    }

    subscriber.service_specific_attribute.devices.push({
      name: '',
      mac: '',
      level: 'PG_13'
    });
  }

  public removeDevice(subscriber: IRCordSubscriber, device: IRCordSubscriberDevice) {
    _.remove(subscriber.service_specific_attribute.devices, {name: device.name});
  }

  public save(subscriber: IRCordSubscriber) {
    const item: any = angular.copy(subscriber);

    delete item.updated;

    _.forEach(Object.keys(item), prop => {
      if (prop.indexOf('-formatted') > -1 || prop.indexOf('_ptr') > -1) {
        delete item[prop];
      }
    });

    item.service_specific_attribute = JSON.stringify(item.service_specific_attribute);
    item.$save()
      .then(() => {
        this.toastr.success(`Subscriber successfully saved`);
      })
      .catch(e => {
        this.toastr.error(`Error while saving subscriber`);
        console.error(e);
      });
  }

  private parseSubscribers(subscribers: IRCordSubscriber) {
    return _.map(subscribers, (s) => {
      if (angular.isString(s.service_specific_attribute)) {
        try {
          s.service_specific_attribute = JSON.parse(s.service_specific_attribute);
        } catch (e) {
          s.service_specific_attribute = {};
        }
      }
      return s;
    });
  }

  $onDestroy() {
    this.selectedSubscriber.service_specific_attribute = JSON.stringify(this.selectedSubscriber.service_specific_attribute);
  }
}

export const rcordSubscriberDashboard: angular.IComponentOptions = {
  template: require('./subscriber-dashboard.html'),
  controllerAs: 'vm',
  controller: RcordSubscriberDashboardCtrl
}
