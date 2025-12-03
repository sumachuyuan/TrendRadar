import os
import tempfile
from datetime import datetime
from pathlib import Path
from rss.storage import RSSStorage
from rss.models import RSSFeed, RSSItem


class TestRSSStorage:
    """RSS存储单元测试"""

    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录作为测试存储位置
        self.temp_dir = tempfile.mkdtemp()
        self.storage = RSSStorage(base_dir=self.temp_dir)

    def teardown_method(self):
        """清理测试环境"""
        # 递归删除临时目录
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_ensure_directory_exists(self):
        """测试确保存储目录存在"""
        # 验证目录已创建
        assert os.path.exists(self.temp_dir)
        assert os.path.isdir(self.temp_dir)

    def test_get_file_path(self):
        """测试获取RSS文件路径"""
        # 测试默认日期
        file_path = self.storage._get_file_path("test")
        assert str(file_path).endswith("/test.xml")
        assert file_path.parent == Path(self.temp_dir)

        # 测试指定日期
        test_date = datetime(2023, 12, 25)
        file_path = self.storage._get_file_path("test", test_date)
        assert str(file_path).endswith("/test.xml")
        assert file_path.parent == Path(self.temp_dir)

    def test_generate_guid(self):
        """测试生成唯一标识"""
        # 测试基本功能
        title = "测试标题"
        link = "https://example.com"
        pub_date = datetime.now()
        guid = self.storage._generate_guid(title, link, pub_date)
        assert isinstance(guid, str)
        assert len(guid) == 32  # MD5哈希长度

        # 测试相同输入生成相同GUID
        guid2 = self.storage._generate_guid(title, link, pub_date)
        assert guid == guid2

        # 测试不同输入生成不同GUID
        guid3 = self.storage._generate_guid("不同标题", link, pub_date)
        assert guid != guid3

    def test_save_rss_feed(self):
        """测试保存RSS Feed到文件"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 保存RSS Feed
        file_path = self.storage.save_rss_feed(feed, "test")

        # 验证文件已创建
        assert os.path.exists(file_path)
        assert os.path.isfile(file_path)
        assert str(file_path).endswith("/test.xml")

        # 验证文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "<rss version=\"2.0\">" in content
        assert "<title>测试Feed</title>" in content

    def test_save_rss_by_keyword(self):
        """测试根据关键词保存RSS"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 添加条目
        item = RSSItem(
            title="测试标题",
            link="https://example.com",
            description="测试描述",
            pub_date=datetime.now(),
            guid="test-guid",
            keywords=["test"]
        )
        feed.add_item(item)

        # 保存RSS
        file_path = self.storage.save_rss_by_keyword(feed, "test")

        # 验证文件已创建
        assert os.path.exists(file_path)
        assert os.path.isfile(file_path)
        assert str(file_path).endswith("/test.xml")

    def test_save_multiple_feeds(self):
        """测试保存多个关键词的RSS"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 添加多个关键词的条目
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

        # 保存多个关键词的RSS
        saved_files = self.storage.save_multiple_feeds(feed)

        # 验证文件已创建
        assert len(saved_files) == 3  # keyword1, keyword2, all
        assert "keyword1" in saved_files
        assert "keyword2" in saved_files
        assert "all" in saved_files

        for file_path in saved_files.values():
            assert os.path.exists(file_path)
            assert os.path.isfile(file_path)

    def test_read_rss(self):
        """测试读取RSS内容"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 保存RSS Feed
        self.storage.save_rss_feed(feed, "test")

        # 读取RSS内容
        rss_content = self.storage.read_rss("test")

        # 验证读取结果
        assert rss_content is not None
        assert isinstance(rss_content, str)
        assert "<rss version=\"2.0\">" in rss_content

        # 测试读取不存在的RSS
        rss_content = self.storage.read_rss("not_exists")
        assert rss_content is None

    def test_list_available_keywords(self):
        """测试列出可用的RSS关键词"""
        # 初始状态应该为空
        keywords = self.storage.list_available_keywords()
        assert isinstance(keywords, list)
        assert len(keywords) == 0

        # 保存几个RSS文件
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )
        self.storage.save_rss_feed(feed, "keyword1")
        self.storage.save_rss_feed(feed, "keyword2")
        self.storage.save_rss_feed(feed, "keyword3")

        # 再次列出可用关键词
        keywords = self.storage.list_available_keywords()
        assert isinstance(keywords, list)
        assert len(keywords) == 3
        assert "keyword1" in keywords
        assert "keyword2" in keywords
        assert "keyword3" in keywords

    def test_get_rss_history(self):
        """测试获取RSS历史记录"""
        # 保存RSS文件
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )
        self.storage.save_rss_feed(feed, "test")

        # 获取历史记录
        history = self.storage.get_rss_history("test")

        # 验证历史记录
        assert isinstance(history, list)
        assert len(history) == 1
        assert history[0].name == "test.xml"
        assert history[0].parent == Path(self.temp_dir)

        # 测试获取不存在的RSS历史记录
        history = self.storage.get_rss_history("not_exists")
        assert isinstance(history, list)
        assert len(history) == 0

    def test_is_duplicate(self):
        """测试检查RSS条目是否重复"""
        # 创建RSSItem
        item = RSSItem(
            title="测试标题",
            link="https://example.com",
            description="测试描述",
            pub_date=datetime.now(),
            guid="test-guid"
        )

        # 测试不存在的GUID
        existing_guids = set()
        is_duplicate = self.storage.is_duplicate(item, existing_guids)
        assert is_duplicate is False

        # 测试已存在的GUID
        existing_guids.add("test-guid")
        is_duplicate = self.storage.is_duplicate(item, existing_guids)
        assert is_duplicate is True

    def test_add_item_to_feed(self):
        """测试添加RSS条目到Feed"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )

        # 创建RSSItem
        item = RSSItem(
            title="测试标题",
            link="https://example.com",
            description="测试描述",
            pub_date=datetime.now(),
            guid="test-guid"
        )

        # 测试添加新条目
        existing_guids = set()
        result = self.storage.add_item_to_feed(feed, item, existing_guids)
        assert result is True
        assert len(feed.items) == 1
        assert feed.items[0] == item

        # 测试添加重复条目
        result = self.storage.add_item_to_feed(feed, item, existing_guids)
        assert result is True  # 注意：这个方法目前没有检查重复，只是添加
        assert len(feed.items) == 2
