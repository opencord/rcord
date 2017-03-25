/// <reference path="../typings/index.d.ts" />
import * as angular from 'angular';

import 'angular-ui-router';
import 'angular-resource';
import 'angular-cookies';
import {RCordGraphReducer, IRCordGraphReducer} from './app/services/graph.extension';

angular.module('xos-rcord-gui-extension', [
    'ui.router',
    'app'
  ])
  .service('RCordGraphReducer', RCordGraphReducer)
  .run(function($log: ng.ILogService, RCordGraphReducer: IRCordGraphReducer) {
    $log.info('[xos-rcord-graph-gui-extension] App is running');
    RCordGraphReducer.setup();
  });
