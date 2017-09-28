
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


/// <reference path="../typings/index.d.ts" />
import * as angular from 'angular';

import 'angular-ui-router';
import 'angular-resource';
import 'angular-cookies';
import 'angularjs-slider';
import '../node_modules/angularjs-slider/dist/rzslider.scss';

import {RCordGraphReducer, IRCordGraphReducer} from './app/services/graph.extension';
import {rcordSubscriberDashboard} from './app/subscriber-dashboard/subscriber-dashboard.component';

angular.module('xos-rcord-gui-extension', [
    'ui.router',
    'app',
    'rzModule'
  ])
  .service('RCordGraphReducer', RCordGraphReducer)
  .component('rcordSubscriberDashboard', rcordSubscriberDashboard)
  .run(function($log: ng.ILogService, RCordGraphReducer: IRCordGraphReducer, XosNavigationService: any, XosRuntimeStates: any, $state: ng.ui.IStateService) {
    $log.info('[xos-rcord-graph-gui-extension] App is running');
    RCordGraphReducer.setup();

    XosRuntimeStates.addState(`xos.rcord`, {
      url: 'rcord',
      parent: 'xos',
      abstract: true,
      template: '<div ui-view></div>'
    });

    XosRuntimeStates.addState(`xos.rcord.dashboard`, {
      url: '/dashboard',
      parent: 'xos.rcord',
      component: 'rcordSubscriberDashboard'
    });

    window.setTimeout(() => {
      $log.info('[xos-rcord-graph-gui-extension] Adding nav item')
      XosNavigationService.add({
        label: 'Dashboard',
        state: 'xos.rcord.dashboard',
        parent: 'xos.rcord'
      });
    }, 5000);
  });
