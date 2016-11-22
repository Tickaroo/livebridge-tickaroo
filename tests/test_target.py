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
import asynctest
import urllib.parse
from asynctest import MagicMock
from livebridge.base import BaseTarget, BasePost, TargetResponse
from livebridge_tickaroo.common import TickarooClient
from livebridge_tickaroo import TickarooTarget
from tests import load_json


class TickarooTargetTests(asynctest.TestCase):

    def setUp(self):
        self.client_id = "ABC"
        self.client_secret = "CBA"
        self.ticker_id = "1234"
        self.client = TickarooTarget(config={"auth": {"client_id":self.client_id, "client_secret":self.client_secret}, "ticker_id": self.ticker_id})

    @asynctest.ignore_loop
    def test_init(self):
        assert self.client.type == "tickaroo"
        assert self.client.client_id == "ABC"
        assert self.client.client_secret == "CBA"
        assert self.client.target_id == "1234"
        assert issubclass(TickarooTarget, BaseTarget) == True
        assert issubclass(TickarooTarget, TickarooClient) == True
        assert isinstance(self.client, BaseTarget) == True

    @asynctest.ignore_loop
    def test_get_event_id(self):
        post_data = load_json('post_to_convert.json')

        post = BasePost(post_data)
        post.target_doc = {"event_local_id": "xyz"}
        assert self.client.get_event_id(post) == "xyz"

        post.target_doc = {}
        assert self.client.get_event_id(post) == None

    async def test_build_url(self):
        url = self.client._build_url("test", {"additional" : "true"})
        query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        assert self.client.client_id == query["client_id"][0]
        assert self.client.client_secret == query["client_secret"][0]
        assert query["additional"][0] == "true"

    async def test_post_item(self):
        api_res = {"_type" : "Tik::Model::Event", "local_id":"xyz"}
        self.client._post =  asynctest.CoroutineMock(return_value=api_res)
        post = MagicMock()
        post.images = []
        post.content = "Test"
        resp = await self.client.post_item(post)
        assert resp == api_res

    async def test_handle_extras(self):
        resp = await self.client.handle_extras({})
        assert resp == None
