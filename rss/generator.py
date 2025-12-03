import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional
from xml.dom import minidom

from rss.models import RSSFeed, RSSItem


class RSSGenerator:
    """RSS生成器，负责生成符合RSS 2.0标准的XML内容"""

    def __init__(self):
        self.rss_version = "2.0"

    @staticmethod
    def format_rfc822_date(date: datetime) -> str:
        """将datetime对象格式化为RFC 822标准日期字符串"""
        # RFC 822格式：Wed, 02 Oct 2002 13:00:00 GMT
        return date.strftime("%a, %d %b %Y %H:%M:%S GMT")

    @staticmethod
    def escape_xml_chars(text: str) -> str:
        """转义XML特殊字符"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def generate_rss(self, feed: RSSFeed) -> str:
        """生成RSS 2.0 XML字符串"""
        # 创建根元素
        rss = ET.Element("rss", version=self.rss_version)
        channel = ET.SubElement(rss, "channel")

        # 添加channel元素
        ET.SubElement(channel, "title").text = self.escape_xml_chars(feed.title)
        ET.SubElement(channel, "link").text = feed.link
        ET.SubElement(channel, "description").text = self.escape_xml_chars(feed.description)
        ET.SubElement(channel, "language").text = feed.language
        ET.SubElement(channel, "pubDate").text = self.format_rfc822_date(feed.pub_date)
        ET.SubElement(channel, "lastBuildDate").text = self.format_rfc822_date(feed.last_build_date)
        ET.SubElement(channel, "generator").text = feed.generator

        # 添加items
        for item in feed.items:
            item_elem = ET.SubElement(channel, "item")
            ET.SubElement(item_elem, "title").text = self.escape_xml_chars(item.title)
            ET.SubElement(item_elem, "link").text = item.link
            ET.SubElement(item_elem, "description").text = self.escape_xml_chars(item.description)
            ET.SubElement(item_elem, "pubDate").text = self.format_rfc822_date(item.pub_date)
            ET.SubElement(item_elem, "guid", isPermaLink="false").text = item.guid

            # 添加可选字段
            if item.source_id and item.source_name:
                ET.SubElement(item_elem, "source", url=f"https://trendradar.example.com/{item.source_id}").text = item.source_name
            if item.rank:
                ET.SubElement(item_elem, "category").text = f"Rank: {item.rank}"
            for keyword in item.keywords:
                ET.SubElement(item_elem, "category").text = keyword

        # 生成XML字符串并美化格式
        rough_string = ET.tostring(rss, encoding="utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    def generate_rss_by_keyword(self, feed: RSSFeed, keyword: str) -> str:
        """根据关键词生成RSS"""
        # 创建新的RSSFeed对象，只包含匹配关键词的条目
        filtered_feed = RSSFeed(
            title=f"{feed.title} - {keyword}",
            link=f"{feed.link}?keyword={keyword}",
            description=f"{feed.description} - {keyword}相关内容",
            pub_date=feed.pub_date,
            language=feed.language,
            generator=feed.generator,
            last_build_date=feed.last_build_date
        )

        # 添加匹配的条目
        for item in feed.get_items_by_keyword(keyword):
            filtered_feed.add_item(item)

        # 生成RSS
        return self.generate_rss(filtered_feed)

    def generate_multiple_feeds(self, feeds: List[RSSFeed]) -> dict:
        """生成多个RSS Feed，返回关键词到RSS内容的映射"""
        return {feed.title: self.generate_rss(feed) for feed in feeds}

    def validate_rss(self, rss_content: str) -> bool:
        """验证RSS内容是否符合XML格式"""
        try:
            ET.fromstring(rss_content)
            return True
        except ET.ParseError:
            return False
