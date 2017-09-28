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

class rcordSubscriberDashboardCtrl {

  static $inject = [
    'toastr',
    'XosModelStore',
    'XosModeldefsCache'
  ];

  public levelOptions = [];
  public subscribers = [];
  public statusFieldOptions = [];
  public slider = {
    floor: 0,
    ceil: 1000000000,
    translate: (value) => {
      return Math.floor(value / 1000000);
    }
  };

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

  public addDevice(subscriber) {
    subscriber.service_specific_attribute.devices.push({
      name: '',
      mac: '',
      level: 'PG_13'
    })
  }

  public removeDevice(subscriber, device) {
    _.remove(subscriber.service_specific_attribute.devices, {name:device.name})
  }

  public save(subscriber) {
    console.log(subscriber);
    const item: any = angular.copy(subscriber);
    item.service_specific_attribute = JSON.stringify(item.service_specific_attribute);
    item.$save()
      .then(() => {
        this.toastr.success(`Subscriber successfully saved`);
      });
  }

  private parseSubscribers(subscribers) {
    return _.map(subscribers, (s) => {
      if (angular.isString(s.service_specific_attribute)) {
        s.service_specific_attribute = JSON.parse(s.service_specific_attribute);
      }
      return s;
    })
  }
}

export const rcordSubscriberDashboard: angular.IComponentOptions = {
  template: require('./subscriber-dashboard.html'),
  controllerAs: 'vm',
  controller: rcordSubscriberDashboardCtrl
};