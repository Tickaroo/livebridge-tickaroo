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
import bleach
import logging
import json
import re
import aiohttp
from dateutil.parser import parse as parse_date
from bs4 import BeautifulSoup

from livebridge.base import BaseConverter, ConversionResult

import logging

logger = logging.getLogger(__name__)

class LiveblogTickarooConverter(BaseConverter):

    source = "liveblog"
    target = "tickaroo"
    
    TAGS_TO_ATTRS = {"a" : "Tik::ApiModel::Text::RefSpan", "b" : "Tik::ApiModel::Text::BoldSpan", "i" : "Tik::ApiModel::Text::ItalicSpan", "u" : "Tik::ApiModel::Text::UnderlineSpan", "strike" : "Tik::ApiModel::Text::StrikethroughSpan"}
    
    class DomProcessState:
        def __init__(self):
            self.current_index = 0
            self.attribute_stack = []
            
    def _text_length(self, node):
        length = 0
        for s in node.strings:
            length += len(s)
        return length
    
    def _process_nodes(self, node, process_state):
        text_length = 0
        if type(node).__name__ == "NavigableString":
            text_length = len(node)
            process_state.current_index += text_length
        else:
            tag = self.TAGS_TO_ATTRS.get(node.name)
            if tag != None:
                text_length = self._text_length(node)
                res = {"_type" : tag, "start" : process_state.current_index, "end" : process_state.current_index + text_length}
                if node.get("href"):
                    res["ref"] = {"_type" : "Tik::ApiModel::UrlRef", "url" : node.attrs["href"]}
                
                process_state.attribute_stack.append(res)
            
            if node.children != None:
                for child in node.children:
                    self._process_nodes(child, process_state)
            else:
                process_state.current_index += text_length
    
    def _clean_attributes(self, process_state):
        stack = process_state.attribute_stack
        length = len(stack)
        attr_to_delete = []
        for i in range(0, length):
            attr_i = stack[i]
            for n in range(i+1, length):
                attr_n = stack[n]
                if attr_n["start"] == attr_i["end"] and attr_i["_type"] == attr_n["_type"]:
                    if attr_i.get("ref") != attr_n.get("ref"):
                        continue
                    attr_i["end"] = attr_n["end"]
                    attr_to_delete.append(n)
        for i in reversed(attr_to_delete):
            del stack[i]

    async def _process_text(self, text):
        html_nodes = BeautifulSoup("<div>{}</div>".format(text), 'html.parser')
        state = LiveblogTickarooConverter.DomProcessState();
        self._process_nodes(html_nodes, state)
        self._clean_attributes(state)
        return html_nodes.get_text(), state.attribute_stack
        
    def _convert_dom(self, node):
        if type(node).__name__ == "NavigableString":
            return
        if node.contents and node.contents[-1].name == "br":
            node.contents[-1].decompose()
        if node.name == "ol":
            i = 1
            lis = node.find_all("li")
            for li in lis:
                li.insert(0, " {}. ".format(i))
                i += 1
            lis[-1].append("@|@|@") # append magic chars to detect last <li>
        if node.name == "ul":
            lis = node.find_all("li")
            for li in lis:
                li.insert(0, " • ")
            lis[-1].append("@|@|@") # append magic chars to detect last <li>
        for child in node.children:
            self._convert_dom(child)

    async def _convert_text(self, item):
        content = item["item"]["text"]
        content = content.replace("&nbsp;", "?|?|?") # replace nbsp with magic chars to avoid bleach and BS4 to mess up our whitespaces
        content = bleach.clean(content, tags=["p", "br", "b", "i", "u", "strike", "ul", "li", "ol", "a", "div"], strip=True)
        
        content = content.replace("<br>", '<br></br>')
        html_nodes = BeautifulSoup("<div>{}</div>".format(content), 'html.parser')
        
        self._convert_dom(html_nodes)
        content = "".join(str(x) for x in html_nodes.div.contents)
        
        content = content.replace("<ol>", "").replace("</ol>", "")
        content = re.sub(r'[ ]+', ' ', content)
        content = content.replace("?|?|?", " ")
        content = re.sub(r'<b>([ ]*)</b>', r'\1', content)
        content = re.sub(r'<i>([ ]*)</i>', r'\1', content)
        content = re.sub(r'<u>([ ]*)</u>', r'\1', content)
        content = content.replace("<ul>", "").replace("</ul>", "")
        content = content.replace("@|@|@</li>", "") # replace last <li> without newline
        content = content.replace("</li>", "\n")
        content = content.replace("<li>", "")
        content = content.replace("<p>", "")
        content = content.replace("</p>", "\n")
        content = content.replace("<div>", "\n")
        content = content.replace("</div>", "")
        content = content.replace("\n**", " ")
        content = content.replace("*\n*", "\n")
        content = content.replace("<br/>", "\n")
        content = content.replace(" ** ", " ")
        return content.rstrip()

    async def _convert_quote(self, item):
        meta = item["item"]["meta"]
        content = "<b><i>»{}«</i></b>".format(meta.get("quote"))
        if meta.get("credit"):
            content += "\n\n{}".format(meta.get("credit"))
        return content

    async def _convert_image(self, item):
        image = None
        try:
            # handle url
            url = item["item"]["meta"]["media"]["renditions"]["viewImage"]["href"]
            # handle text
            caption = item["item"]["meta"]["caption"]
            credit = item["item"]["meta"]["credit"]
            image = {"_type" : "Tik::Model::Media", "subtype" : "i", "url" : url, "title" : caption, "credit" : credit}
        except Exception as e:
            logger.error("Tickaroo: Fatal error when converting image.")
            logger.exception(e)
        return image

    async def _convert_embed(self, item):
        content = ""
        meta = item["item"]["meta"]
        if meta.get("original_url"):
            return meta["original_url"]
        elif meta.get("html"):
            with aiohttp.ClientSession() as session:
                async with session.post("https://media.tickaroo.com/v2/50b6675694a940db6d000002/web_embed_code.json", data=meta["html"]) as resp:
                    if resp.status == 200:
                        msg = await resp.json()
                        return msg["url"]
        return None
    
    def _create_event_hash(self, post, text, attributes, medias=[], webembeds=[]):
        data = {"_type" : "Tik::Model::Event"}
        if medias:
            data["media"] = medias
        event_info = {"_type" : "Tik::Model::EventInfo::BasicEventInfo", "title" : text, "event_type" : 0}
        if attributes:
            event_info["attributes_json"] = json.dumps({"_type" : "Tik::ApiModel::Text::AttributedText", "text" : text, "attrs" : attributes}, sort_keys=True)
        if webembeds:
            event_info["web_embed_urls"] = webembeds
        data["event_info"] = event_info
        if post.get("_created"):
            data["created_at"] = parse_date(post.get("_created")).timestamp()
        if post.get("sticky"):
            data["highlight"] = "sticky"
        elif post.get("highlight"):
            data["highlight"] = "inplace"
        return data
    

    async def convert(self, post):
        content = ""
        images = []
        try:
            text = ""
            webembeds = []
            medias = []
            for g in post.get("groups", []):
                if g["id"] != "main":
                    continue
                for item in g["refs"]:
                    if item["item"]["item_type"] == "text":
                        if len(text) > 0:
                            text += "\n\n"
                        text += await self._convert_text(item)
                    elif item["item"]["item_type"] == "quote":
                        if len(text) > 0:
                            text += "\n\n"
                        text += await self._convert_quote(item)
                    elif item["item"]["item_type"] == "image":
                        image = await self._convert_image(item)
                        if image:
                            medias.append(image)
                    elif item["item"]["item_type"] == "embed":
                        url = await self._convert_embed(item)
                        if url:
                            webembeds.append(url)
            text, attributes = await self._process_text(text)
            event_hash = self._create_event_hash(post, text, attributes, medias, webembeds)
            content = json.dumps(event_hash)
        except Exception as e:
            logger.error("Converting to tickaroo post failed.")
            logger.exception(e)
        return ConversionResult(content, images)
