# -*- coding: utf-8 -*-
#
# Copyright 2016 Tickaroo GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from livebridge.base import BaseTarget, TargetResponse
from livebridge_tickaroo.common import TickarooClient

logger = logging.getLogger(__name__)

class TickarooTarget(TickarooClient, BaseTarget):

    type = "tickaroo"
    
    def get_event_id(self, post):
        event_id = None
        if post.target_doc:
            event_id = post.target_doc.get("local_id")
        return event_id

    async def post_item(self, post):
        post_url = None
        if self.target_id
            post_url =  self._build_url("write/event/create.json", {"ticker_id" : self.target_id})
        else 
            post_url =  self._build_url("write/event/create.json", {"ticker_local_id" : self.target_local_id})
        response = await self._post(post_url, post.content)
        logger.info("post item response: ".format(response))
        return TargetResponse(response)

    async def update_item(self, post):
        event_id = self.get_event_id(post)
        if not event_id:
            logger.warning("Handling updated item without TARGET-ID: [{}, {}] on {}".format(self.target_id, self.target_local_id, post.id))
            return False

        update_url = self._build_url("write/event/update.json", {"event_local_id" : event_id})
        response = await self._post(update_url, post.content)
        return TargetResponse(response)

    async def delete_item(self, post):
        event_id = self.get_event_id(post)
        if not event_id:
            logger.warning("Handling deleted item without TARGET-ID: [{}, {}] on {}".format(self.target_id, self.target_local_id, post.id))
            return False

        delete_url = self._build_url("write/event/delete.json", {"event_local_id" : event_id})
        response = await self._post(delete_url)
        return TargetResponse(response)

    async def handle_extras(self, post):
        pass
    