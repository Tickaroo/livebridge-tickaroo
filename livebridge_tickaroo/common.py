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
import aiohttp
import logging
import urllib.parse

logger = logging.getLogger(__name__)

class TickarooClient(object):

    type = "tickaroo"

    def __init__(self, *, config={}, **kwargs):
        self.client_id = config.get("auth", {}).get("client_id")
        self.client_secret = config.get("auth", {}).get("client_secret")
        self.target_id = config.get("ticker_id")
        self.endpoint = config.get("endpoint")
        logger.info("TickarooClient created")
        
    def _build_url(self, path, params={}):
        params["client_id"] = self.client_id
        params["client_secret"] = self.client_secret
        return "{}{}?{}".format(self.endpoint, path, urllib.parse.urlencode(params))

    async def _post(self, url, data=[], status=200):
        logger.info("posting data {} {}".format(url, data))
        try:
            logger.debug("POST: {}".format(url))
            with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as resp:
                    if resp.status == status:
                        logger.info("POST successfull response: {}".format(resp))
                        msg = await resp.json()
                        logger.info("POST successfull json: {}".format(msg))
                        return msg
                    else:
                        logger.info("POST request failed with status [{}], expected {}".format(resp.status, status))
                        logger.info(await resp.text())
        except aiohttp.ClientOSError as e:
            logger.error("POST request failed for [{}, {}] on {}".format(self.target_id, self.target_local_id, self.endpoint))
            logger.error(e)
        return {}
          
