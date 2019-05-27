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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multistructlog import create_logger
from xossynchronizer.modelaccessor import RCORDSubscriber, model_accessor
from xossynchronizer.steps.syncstep import SyncStep
from xosconfig import Config

log = create_logger(Config().get("logging"))

class SyncRCORDSubscriber(SyncStep):
    provides = [RCORDSubscriber]

    observes = RCORDSubscriber

    #TODO: (Blocked by SEBA-694) : Add API calls that will be implemented by SEBA-694 to flush the Sadis cache when a subscriber changes or is removed.

    def sync_record(self, model):
        log.info('Synching RCORDSubscriber', object=str(model), **model.tologdict())

    def delete_record(self, model):
        log.info('Deleting RCORDSubscriber', object=str(model), **model.tologdict())
