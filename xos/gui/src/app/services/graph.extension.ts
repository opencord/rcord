
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


import * as $ from 'jquery';
import * as _ from 'lodash';

export interface IRCordGraphReducer {
  setup(): void;
}

export class RCordGraphReducer implements IRCordGraphReducer {

  static $inject = [
    'XosServiceGraphExtender'
  ];

  constructor(
    private XosServiceGraphExtender: any
  ) {

  }

  public setup() {
    this.XosServiceGraphExtender.register('coarse', 'ecord-local', (graph: any): any => {
      graph.nodes = this.positionCoarseNodes(graph.nodes);
      return {
        nodes: graph.nodes,
        links: graph.links
      };
    });
  }

  private getSvgDimensions(graph: string): {width: number, height: number} {
    return {
      width: $(`${graph} svg`).width(),
      height: $(`${graph} svg`).height()
    };
  }

  private positionCoarseNodes(nodes: any[]): any[] {
    // getting distance between nodes
    const hStep = this.getSvgDimensions('xos-coarse-tenancy-graph').width / 4;
    const vStep = this.getSvgDimensions('xos-coarse-tenancy-graph').height / 5;

    const vtr = _.find(nodes, {label: 'vtr'});
    if (vtr) {
      vtr.x = hStep * 2;
      vtr.y = vStep * 1;
      vtr.fixed = true;
    }

    const rcord = _.find(nodes, {label: 'rcord'});
    if (rcord) {
      rcord.x = hStep * 0.5;
      rcord.y = vStep * 2;
      rcord.fixed = true;
    }

    const volt = _.find(nodes, {label: 'volt'});
    if (volt) {
      volt.x = hStep * 1;
      volt.y = vStep * 2;
      volt.fixed = true;
    }

    const vsg = _.find(nodes, {label: 'vsg'});
    if (vsg) {
      vsg.x = hStep * 2;
      vsg.y = vStep * 2;
      vsg.fixed = true;
    }

    const vrouter = _.find(nodes, {label: 'vrouter'});
    if (vrouter) {
      vrouter.x = hStep * 3;
      vrouter.y = vStep * 2;
      vrouter.fixed = true;
    }

    const addressmanager = _.find(nodes, {label: 'addressmanager'});
    if (addressmanager) {
      addressmanager.x = hStep * 2.5;
      addressmanager.y = vStep * 1.5;
      addressmanager.fixed = true;
    }

    const oc = _.find(nodes, {label: 'ONOS_CORD'});
    if (oc) {
      oc.x = hStep + (hStep / 2);
      oc.y = vStep * 3;
      oc.fixed = true;
    }

    const vtn = _.find(nodes, {label: 'vtn'});
    if (vtn) {
      vtn.x = hStep * 1.5;
      vtn.y = vStep * 4;
      vtn.fixed = true;
    }

    const of = _.find(nodes, {label: 'ONOS_Fabric'});
    if (of) {
      of.x = hStep * 2.5;
      of.y = vStep * 3;
      of.fixed = true;
    }

    const fabric = _.find(nodes, {label: 'fabric'});
    if (fabric) {
      fabric.x = hStep * 2.5;
      fabric.y = vStep * 4;
      fabric.fixed = true;
    }

    const exampleservice = _.find(nodes, {label: 'exampleservice'});
    if (exampleservice) {
      exampleservice.x = hStep * 3.5;
      exampleservice.y = vStep * 4.5;
      exampleservice.fixed = true;
    }

    return nodes;
  }
}
