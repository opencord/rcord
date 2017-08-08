
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


webpackJsonp([0],{121:function(module,exports){"use strict";exports.__esModule=!0;var ECordFineGrainedGraphReducer=function(){function ECordFineGrainedGraphReducer(XosServiceGraphExtender){this.XosServiceGraphExtender=XosServiceGraphExtender,this.nodes=[{id:"subscriber~1",label:"Enterprise",type:"subscriber"},{id:"tenant~1",label:"1",type:"tenant"},{id:"service~1",label:"vEE",type:"service"},{id:"tenant~2",label:"2",type:"tenant"},{id:"service~2",label:"vEG",type:"service"},{id:"tenant~3",label:"3",type:"tenant"},{id:"service~3",label:"vROUTER",type:"service"},{id:"tenant~4",label:"4",type:"tenant"},{id:"network~1",label:"public",type:"network"},{id:"tenant~5",label:"5",type:"tenant"},{id:"service~4",label:"vNodLocal",type:"service"},{id:"tenant~6",label:"6",type:"tenant"},{id:"network~2",label:"enterprise",type:"network"}],this.links=[{id:"service~1-tenant~1",source:2,target:1},{id:"tenant~1-subscriber~1",source:1,target:0},{id:"service~2-tenant~2",source:4,target:3},{id:"tenant~2-tenant~1",source:3,target:1},{id:"service~3-tenant~3",source:6,target:5},{id:"tenant~3-tenant~2",source:5,target:3},{id:"network~1-tenant~4",source:8,target:7},{id:"tenant~4-tenant~3",source:7,target:5},{id:"service~4-tenant~5",source:10,target:9},{id:"tenant~5-tenant~1",source:9,target:1},{id:"network~2-tenant~6",source:12,target:11},{id:"tenant~6-tenant~5",source:11,target:9}]}return ECordFineGrainedGraphReducer.prototype.setup=function(){var _this=this;this.XosServiceGraphExtender.register("finegrained","ecord-local",function(){return{nodes:_this.nodes,links:_this.links}})},ECordFineGrainedGraphReducer}();ECordFineGrainedGraphReducer.$inject=["XosServiceGraphExtender"],exports.ECordFineGrainedGraphReducer=ECordFineGrainedGraphReducer},122:function(module,exports){"use strict";function routesConfig($stateProvider,$locationProvider){$locationProvider.html5Mode(!1).hashPrefix("")}exports.__esModule=!0,exports["default"]=routesConfig},478:function(module,exports,__webpack_require__){"use strict";exports.__esModule=!0;var angular=__webpack_require__(48);__webpack_require__(47),__webpack_require__(46),__webpack_require__(45);var routes_1=__webpack_require__(122),fine_grained_graph_extension_1=__webpack_require__(121);angular.module("xos-ecord-local-gui-extension",["ui.router","app"]).config(routes_1["default"]).service("ECordFineGrainedGraphReducer",fine_grained_graph_extension_1.ECordFineGrainedGraphReducer).run(["$log","RCordGraphReducer",function($log, ECordFineGrainedGraphReducer){$log.info("[xos-ecord-local-gui-extension] App is running"),ECordFineGrainedGraphReducer.setup()}])}},[478]);