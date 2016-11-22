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
import os.path
import json
from livebridge_tickaroo import LiveblogTickarooConverter
from tests import load_json

class TickarooConverterTest(asynctest.TestCase):

    def setUp(self):
        self.converter = LiveblogTickarooConverter()

    async def test_simple_conversion(self):
        post = load_json('post_to_convert.json')
        res = await self.converter.convert(post)
        assert len(res.content) >= 1
        
        json_hash_exp = load_json('post_to_expect.json')
        json_hash_res = json.loads(res.content)
        assert json_hash_exp == json_hash_res
        
        await self.converter.remove_images(res.images)

        # let it fail with catched exception
        del post["groups"][1]["refs"]
        res = await self.converter.convert(post)
        assert res.content == ""
        assert res.images == []

    async def test_convert_quote(self):
        item = {"item": {"meta": {"quote": "Zitat", "credit": "Urheber"}}}
        res = await self.converter._convert_quote(item)
        assert res == "<b><i>»Zitat«</i></b>\n\nUrheber"
        
    async def test_convert_text(self):
        text = "<p>Test Whitespace&nbsp;<b>&nbsp; </b><b> BoldText <br><br></b>NormalText <b><br></b>  <i>ItalicText</i> <strike>Strike</strike>baz<br></p>"
        
        res = await self.converter._convert_text({"item": {"text": text}})
        print(res)
        assert res == "Test Whitespace  <b> BoldText \n</b>NormalText <b>\n</b> <i>ItalicText</i> <strike>Strike</strike>baz"
        
    async def test_highlight(self):
        """docstring for test_sticky"""
        post = load_json('post_to_convert.json')
        res = await self.converter.convert(post)
        assert len(res.content) >= 1
        
        json_hash_res = json.loads(res.content)
        assert json_hash_res.get("highlight") == None # "sticky"
        
        # should be inline
        post["highlight"] = True
        res = await self.converter.convert(post)
        assert len(res.content) >= 1
        
        json_hash_res = json.loads(res.content)
        assert json_hash_res["highlight"] == "inplace"
        
        # keep sticky, ignore highlight
        post["sticky"] = True
        res = await self.converter.convert(post)
        assert len(res.content) >= 1
        
        json_hash_res = json.loads(res.content)
        assert json_hash_res["highlight"] == "sticky"
        
        
    # async def test_convert_image(self):
    #     assert True == False
    #
    # async def test_convert_embed(self):
    #     assert True == False

