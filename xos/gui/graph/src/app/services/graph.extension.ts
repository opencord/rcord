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
    this.XosServiceGraphExtender.register('finegrained', 'ecord-local', (graph): any => {
      return graph;
    });

    this.XosServiceGraphExtender.register('coarse', 'ecord-local', (graph: any): any => {
      graph.nodes = this.positionCoarseNodes(graph.nodes);
      return {
        nodes: graph.nodes,
        links: graph.links
      };
    });
  }

  private getSvgDimensions(graph: string): {width: number, heigth: number} {
    return {
      width: $(`${graph} svg`).width(),
      heigth: $(`${graph} svg`).height()
    };
  }

  private positionCoarseNodes(nodes: any[]): any[] {
    // getting distance between nodes
    const hStep = this.getSvgDimensions('xos-coarse-tenancy-graph').width / 4;
    const vStep = this.getSvgDimensions('xos-coarse-tenancy-graph').heigth / 4;

    const vtr = _.find(nodes, {label: 'vtr'});
    if (vtr) {
      vtr.x = hStep * 2;
      vtr.y = vStep * 1;
      vtr.fixed = true;
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

    const oc = _.find(nodes, {label: 'ONOS_CORD'});
    if (oc) {
      oc.x = hStep + (hStep / 2);
      oc.y = vStep * 3;
      oc.fixed = true;
    }

    const of = _.find(nodes, {label: 'ONOS_Fabric'});
    if (of) {
      of.x = (hStep * 2) + (hStep / 2);
      of.y = vStep * 3;
      of.fixed = true;
    }

    return nodes;
  }
}
