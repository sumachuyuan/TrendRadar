import pytest
from datetime import datetime
from rss.generator import RSSGenerator
from rss.models import RSSFeed, RSSItem


class TestRSSGenerator:
    """RSS生成器单元测试"""

    def setup_method(self):
        """设置测试环境"""
        self.generator = RSSGenerator()

    def test_format_rfc822_date(self):
        """测试RFC 822日期格式转换"""
        test_date = datetime(2023, 12, 25, 10, 30, 45)
        formatted_date = self.generator.format_rfc822_date(test_date)
        # 预期格式: "Mon, 25 Dec 2023 10:30:45 GMT"
        assert "25 Dec 2023 10:30:45 GMT" in formatted_date

    def test_escape_xml_chars(self):
        """测试XML特殊字符转义"""
        test_text = '<test> & "text" \'with\' special chars >'
        escaped_text = self.generator.escape_xml_chars(test_text)
        assert escaped_text == '&lt;test&gt; &amp; &quot;text&quot; &apos;with&apos; special chars &gt;'

    def test_generate_rss_basic(self):
        """测试生成基本RSS内容"""
        # 创建简单的RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 生成RSS内容
        rss_content = self.generator.generate_rss(feed)

        # 验证基本结构
        assert "<rss version=\"2.0\">" in rss_content
        assert "<channel>" in rss_content
        assert "</channel>" in rss_content
        assert "</rss>" in rss_content
        assert "<title>测试Feed</title>" in rss_content
        assert "<link>https://example.com/feed</link>" in rss_content
        assert "<description>测试Feed描述</description>" in rss_content
        assert "<generator>TrendRadar RSS Generator</generator>" in rss_content

    def test_generate_rss_with_items(self):
        """测试生成带条目RSS内容"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 添加两个条目
        for i in range(2):
            item = RSSItem(
                title=f"测试标题{i+1}",
                link=f"https://example.com/{i+1}",
                description=f"测试描述{i+1}",
                pub_date=datetime.now(),
                guid=f"test-guid-{i+1}",
                keywords=[f"keyword{i+1}"]
            )
            feed.add_item(item)

        # 生成RSS内容
        rss_content = self.generator.generate_rss(feed)

        # 验证条目存在
        assert "<item>" in rss_content
        assert "</item>" in rss_content
        assert "<title>测试标题1</title>" in rss_content
        assert "<title>测试标题2</title>" in rss_content
        assert "<link>https://example.com/1</link>" in rss_content
        assert "<link>https://example.com/2</link>" in rss_content
        assert "<guid isPermaLink=\"false\">test-guid-1</guid>" in rss_content
        assert "<guid isPermaLink=\"false\">test-guid-2</guid>" in rss_content
        assert "<category>keyword1</category>" in rss_content
        assert "<category>keyword2</category>" in rss_content

    def test_generate_rss_by_keyword(self):
        """测试按关键词生成RSS内容"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 添加不同关键词的条目
        item1 = RSSItem(
            title="测试标题1",
            link="https://example.com/1",
            description="测试描述1",
            pub_date=datetime.now(),
            guid="test-guid-1",
            keywords=["keyword1"]
        )

        item2 = RSSItem(
            title="测试标题2",
            link="https://example.com/2",
            description="测试描述2",
            pub_date=datetime.now(),
            guid="test-guid-2",
            keywords=["keyword2"]
        )

        item3 = RSSItem(
            title="测试标题3",
            link="https://example.com/3",
            description="测试描述3",
            pub_date=datetime.now(),
            guid="test-guid-3",
            keywords=["keyword1", "keyword2"]
        )

        feed.add_item(item1)
        feed.add_item(item2)
        feed.add_item(item3)

        # 按keyword1生成RSS
        rss_content = self.generator.generate_rss_by_keyword(feed, "keyword1")

        # 验证只包含keyword1的条目
        assert "<title>测试Feed - keyword1</title>" in rss_content
        assert "<link>https://example.com/feed?keyword=keyword1</link>" in rss_content
        assert "<title>测试标题1</title>" in rss_content
        assert "<title>测试标题3</title>" in rss_content
        assert "<title>测试标题2</title>" not in rss_content  # 不包含keyword2的条目

        # 按keyword2生成RSS
        rss_content = self.generator.generate_rss_by_keyword(feed, "keyword2")

        # 验证只包含keyword2的条目
        assert "<title>测试Feed - keyword2</title>" in rss_content
        assert "<link>https://example.com/feed?keyword=keyword2</link>" in rss_content
        assert "<title>测试标题2</title>" in rss_content
        assert "<title>测试标题3</title>" in rss_content
        assert "<title>测试标题1</title>" not in rss_content  # 不包含keyword1的条目

    def test_validate_rss_valid(self):
        """测试验证有效RSS内容"""
        # 创建简单的RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 生成RSS内容
        rss_content = self.generator.generate_rss(feed)

        # 验证RSS格式
        is_valid = self.generator.validate_rss(rss_content)
        assert is_valid is True

    def test_validate_rss_invalid(self):
        """测试验证无效RSS内容"""
        # 无效的RSS内容
        invalid_rss = '<rss version=\"2.0\"><channel><title>Invalid</title></rss>'

        # 验证RSS格式
        is_valid = self.generator.validate_rss(invalid_rss)
        assert is_valid is False

    def test_generate_rss_with_source_info(self):
        """测试生成带有源信息的RSS内容"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 创建带有源信息的Item
        item = RSSItem(
            title="测试标题",
            link="https://example.com",
            description="测试描述",
            pub_date=datetime.now(),
            guid="test-guid",
            source_id="test-source",
            source_name="测试来源",
            rank=1,
            mobile_link="https://m.example.com",
            keywords=["test"]
        )

        feed.add_item(item)

        # 生成RSS内容
        rss_content = self.generator.generate_rss(feed)

        # 验证源信息存在
        assert "<source url=\"https://trendradar.example.com/test-source\">测试来源</source>" in rss_content
        assert "<category>Rank: 1</category>" in rss_content
        assert "<category>test</category>" in rss_content
