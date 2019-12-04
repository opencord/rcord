# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, sys
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multistructlog import create_logger
from xossynchronizer.modelaccessor import RCORDSubscriber, model_accessor
from xossynchronizer.steps.syncstep import SyncStep
from xosconfig import Config
from requests.auth import HTTPBasicAuth

log = create_logger(Config().get("logging"))

class SyncRCORDSubscriber(SyncStep):
    provides = [RCORDSubscriber]

    observes = RCORDSubscriber

    def sync_record(self, model):
        log.info('Synching RCORDSubscriber', object=str(model), **model.tologdict())
        self.delete_sadis_subscriber( self , model)

    def delete_record(self, model):
        log.info('Deleting RCORDSubscriber', object=str(model), **model.tologdict())
        self.delete_sadis_subscriber( self , model)

    @staticmethod
    def delete_sadis_subscriber( self,  model):
        log.info('Deleting sadis subscriber cache', object=str(model), **model.tologdict())
        onos = self.get_rcord_onos_info( self , model )
        url = onos['url'] + '/onos/sadis/cache/subscriber/' + str(model.onu_device)
        r = requests.delete(url, auth=HTTPBasicAuth(onos['user'], onos['pass']))
        if r.status_code != 204:
            self.log.info("Failed to remove sadis subscriber in ONOS")
        log.info("ONOS response", res=r.text)

    @staticmethod
    def get_rcord_onos_info( self, model ):
        # get rcord service
        rcord = model.owner

        # get the rcord onos service
        rcord_onos = [s.leaf_model for s in rcord.provider_services if "onos" in s.name.lower()]

        if len(rcord_onos) == 0:
            raise Exception('Cannot find ONOS service in provider_services of rcord')

        rcord_onos = rcord_onos[0]
        return {
            'url': SyncRCORDSubscriber.format_url( "%s:%s" % (rcord_onos.rest_hostname, rcord_onos.rest_port)),
            'user': rcord_onos.rest_username,
            'pass': rcord_onos.rest_password
        }

    @staticmethod
    def format_url(url):
        if 'http' in url:
            return url
        else:
            return 'http://%s' % url

