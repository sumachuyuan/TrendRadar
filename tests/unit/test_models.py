import pytest
from datetime import datetime
from rss.models import RSSItem, RSSFeed


class TestRSSModels:
    """RSS模型单元测试"""

    def test_rss_item_creation(self):
        """测试RSSItem创建"""
        # 测试数据
        title = "测试标题"
        link = "https://example.com"
        description = "测试描述"
        pub_date = datetime.now()
        guid = "test-guid"

        # 创建RSSItem实例
        item = RSSItem(
            title=title,
            link=link,
            description=description,
            pub_date=pub_date,
            guid=guid
        )

        # 验证属性
        assert item.title == title
        assert item.link == link
        assert item.description == description
        assert item.pub_date == pub_date
        assert item.guid == guid
        assert item.keywords == []
        assert item.rank is None
        assert item.source_id is None
        assert item.source_name is None
        assert item.mobile_link is None

    def test_rss_item_with_optional_fields(self):
        """测试带可选字段的RSSItem创建"""
        # 测试数据
        title = "测试标题"
        link = "https://example.com"
        description = "测试描述"
        pub_date = datetime.now()
        guid = "test-guid"
        source_id = "test-source"
        source_name = "测试来源"
        rank = 1
        mobile_link = "https://m.example.com"
        keywords = ["test", "rss"]

        # 创建RSSItem实例
        item = RSSItem(
            title=title,
            link=link,
            description=description,
            pub_date=pub_date,
            guid=guid,
            source_id=source_id,
            source_name=source_name,
            rank=rank,
            mobile_link=mobile_link,
            keywords=keywords
        )

        # 验证属性
        assert item.source_id == source_id
        assert item.source_name == source_name
        assert item.rank == rank
        assert item.mobile_link == mobile_link
        assert item.keywords == keywords

    def test_rss_feed_creation(self):
        """测试RSSFeed创建"""
        # 测试数据
        title = "测试Feed"
        link = "https://example.com/feed"
        description = "测试Feed描述"
        pub_date = datetime.now()

        # 创建RSSFeed实例
        feed = RSSFeed(
            title=title,
            link=link,
            description=description,
            pub_date=pub_date
        )

        # 验证属性
        assert feed.title == title
        assert feed.link == link
        assert feed.description == description
        assert feed.pub_date == pub_date
        assert feed.last_build_date == pub_date
        assert feed.language == "zh-CN"
        assert feed.generator == "TrendRadar RSS Generator"
        assert len(feed.items) == 0

    def test_rss_feed_add_item(self):
        """测试向RSSFeed添加Item"""
        # 创建Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 创建Item
        item = RSSItem(
            title="测试标题",
            link="https://example.com",
            description="测试描述",
            pub_date=datetime.now(),
            guid="test-guid"
        )

        # 添加Item到Feed
        feed.add_item(item)

        # 验证添加结果
        assert len(feed.items) == 1
        assert feed.items[0] == item

    def test_rss_feed_get_items_by_keyword(self):
        """测试根据关键词获取RSSItem"""
        # 创建Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 创建Items
        item1 = RSSItem(
            title="测试标题1",
            link="https://example.com/1",
            description="测试描述1",
            pub_date=datetime.now(),
            guid="test-guid-1",
            keywords=["test", "rss"]
        )

        item2 = RSSItem(
            title="测试标题2",
            link="https://example.com/2",
            description="测试描述2",
            pub_date=datetime.now(),
            guid="test-guid-2",
            keywords=["test", "python"]
        )

        item3 = RSSItem(
            title="测试标题3",
            link="https://example.com/3",
            description="测试描述3",
            pub_date=datetime.now(),
            guid="test-guid-3",
            keywords=["python", "django"]
        )

        # 添加Items到Feed
        feed.add_item(item1)
        feed.add_item(item2)
        feed.add_item(item3)

        # 测试获取关键词为"test"的Items
        test_items = feed.get_items_by_keyword("test")
        assert len(test_items) == 2
        assert item1 in test_items
        assert item2 in test_items
        assert item3 not in test_items

        # 测试获取关键词为"python"的Items
        python_items = feed.get_items_by_keyword("python")
        assert len(python_items) == 2
        assert item2 in python_items
        assert item3 in python_items
        assert item1 not in python_items

        # 测试获取关键词为"django"的Items
        django_items = feed.get_items_by_keyword("django")
        assert len(django_items) == 1
        assert item3 in django_items

    def test_rss_feed_sort_items_by_date(self):
        """测试按日期排序RSSItem"""
        # 创建Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 创建不同日期的Items
        now = datetime.now()
        item1 = RSSItem(
            title="测试标题1",
            link="https://example.com/1",
            description="测试描述1",
            pub_date=now.replace(hour=10, minute=0, second=0),
            guid="test-guid-1"
        )

        item2 = RSSItem(
            title="测试标题2",
            link="https://example.com/2",
            description="测试描述2",
            pub_date=now.replace(hour=12, minute=0, second=0),
            guid="test-guid-2"
        )

        item3 = RSSItem(
            title="测试标题3",
            link="https://example.com/3",
            description="测试描述3",
            pub_date=now.replace(hour=8, minute=0, second=0),
            guid="test-guid-3"
        )

        # 添加Items到Feed（无序）
        feed.add_item(item1)
        feed.add_item(item2)
        feed.add_item(item3)

        # 测试默认排序（降序）
        feed.sort_items_by_date()
        assert [item.pub_date for item in feed.items] == sorted([item1.pub_date, item2.pub_date, item3.pub_date], reverse=True)
        assert feed.items[0] == item2  # 最新的
        assert feed.items[1] == item1
        assert feed.items[2] == item3  # 最旧的

        # 测试升序排序
        feed.sort_items_by_date(reverse=False)
        assert [item.pub_date for item in feed.items] == sorted([item1.pub_date, item2.pub_date, item3.pub_date])
        assert feed.items[0] == item3  # 最旧的
        assert feed.items[1] == item1
        assert feed.items[2] == item2  # 最新的

    def test_rss_feed_limit_items(self):
        """测试限制RSSItem数量"""
        # 创建Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 添加多个Items
        for i in range(5):
            item = RSSItem(
                title=f"测试标题{i+1}",
                link=f"https://example.com/{i+1}",
                description=f"测试描述{i+1}",
                pub_date=datetime.now(),
                guid=f"test-guid-{i+1}"
            )
            feed.add_item(item)

        # 验证初始数量
        assert len(feed.items) == 5

        # 限制为3个Items
        feed.limit_items(3)
        assert len(feed.items) == 3

        # 限制为0个Items
        feed.limit_items(0)
        assert len(feed.items) == 0

        # 限制数量大于现有数量
        feed.limit_items(10)
        assert len(feed.items) == 0
