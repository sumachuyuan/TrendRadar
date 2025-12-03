import os
import tempfile
from datetime import datetime
from rss.service import RSSService
from rss.models import RSSFeed, RSSItem

class TestRSSService:
    
    """RSS服务单元测试"""

    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录作为测试存储位置
        self.temp_dir = tempfile.mkdtemp()
        # 使用自定义存储目录初始化RSSService
        self.service = RSSService()
        # 替换存储目录为临时目录，便于测试
        self.service.storage.base_dir = os.path.join(self.temp_dir, "rss")
        self.service.storage._ensure_directory_exists()

    def teardown_method(self):
        """清理测试环境"""
        # 递归删除临时目录
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_get_rss_subscriptions(self):
        """测试获取RSS订阅列表"""
        # 初始状态应该为空
        subscriptions = self.service.get_rss_subscriptions()
        assert isinstance(subscriptions, list)
        assert len(subscriptions) == 0

        # 保存几个RSS文件
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )
        self.service.storage.save_rss_feed(feed, "keyword1")
        self.service.storage.save_rss_feed(feed, "keyword2")

        # 再次获取订阅列表
        subscriptions = self.service.get_rss_subscriptions()
        assert isinstance(subscriptions, list)
        assert len(subscriptions) == 2

        # 验证订阅信息
        for subscription in subscriptions:
            assert "keyword" in subscription
            assert "title" in subscription
            assert "link" in subscription
            assert "description" in subscription
            assert subscription["keyword"] in ["keyword1", "keyword2"]

    def test_generate_rss_from_raw_data(self):
        """测试从原始数据生成RSS"""
        # 创建模拟的原始抓取数据
        raw_data = {
            "test-source": {
                "测试标题1": {
                    "ranks": [1],
                    "url": "https://example.com/1",
                    "mobileUrl": "https://m.example.com/1"
                },
                "测试标题2": {
                    "ranks": [2],
                    "url": "https://example.com/2",
                    "mobileUrl": "https://m.example.com/2"
                }
            }
        }
        id_to_name = {"test-source": "测试来源"}

        # 从原始数据生成RSS Feed
        feed = self.service.generate_rss_from_raw_data(raw_data, id_to_name)

        # 验证结果
        assert isinstance(feed, RSSFeed)
        assert len(feed.items) == 2
        assert feed.title == "TrendRadar热点分析"
        assert feed.description == "TrendRadar智能新闻聚合和监控系统生成的RSS Feed（包含全部内容）"

        # 验证条目内容
        for item in feed.items:
            assert isinstance(item, RSSItem)
            assert "测试标题" in item.title
            assert "https://example.com" in item.link
            assert item.source_id == "test-source"
            assert item.source_name == "测试来源"
            assert item.rank in [1, 2]
            assert item.keywords == ["all"]

    def test_generate_rss_feed(self):
        """测试从频率结果生成RSS"""
        # 创建模拟的频率结果
        frequency_results = {
            "keyword1": [
                {
                    "title": "测试标题1",
                    "url": "https://example.com/1",
                    "mobileUrl": "https://m.example.com/1",
                    "id": "test-source",
                    "rank": 1,
                    "count": 2
                }
            ],
            "keyword2": [
                {
                    "title": "测试标题2",
                    "url": "https://example.com/2",
                    "mobileUrl": "https://m.example.com/2",
                    "id": "test-source",
                    "rank": 2,
                    "count": 1
                }
            ]
        }
        id_to_name = {"test-source": "测试来源"}

        # 从频率结果生成RSS Feed
        feed = self.service.generate_rss_feed(frequency_results, id_to_name)

        # 验证结果
        assert isinstance(feed, RSSFeed)
        assert len(feed.items) == 2
        assert feed.title == "TrendRadar热点分析"
        assert feed.description == "TrendRadar智能新闻聚合和监控系统生成的RSS Feed"

        # 验证条目内容
        for item in feed.items:
            assert isinstance(item, RSSItem)
            assert "测试标题" in item.title
            assert "https://example.com" in item.link
            assert item.source_id == "test-source"
            assert item.source_name == "测试来源"
            assert item.rank in [1, 2]
            assert item.keywords in [["keyword1"], ["keyword2"]]

    def test_generate_and_save_rss_raw_data(self):
        """测试使用原始数据生成并保存RSS"""
        # 创建模拟的原始抓取数据
        raw_data = {
            "test-source": {
                "测试标题1": {
                    "ranks": [1],
                    "url": "https://example.com/1",
                    "mobileUrl": "https://m.example.com/1"
                }
            }
        }
        id_to_name = {"test-source": "测试来源"}

        # 生成并保存RSS
        saved_files = self.service.generate_and_save_rss(raw_data, id_to_name, use_raw_data=True)

        # 验证保存结果
        assert isinstance(saved_files, dict)
        assert len(saved_files) == 1
        assert "all" in saved_files
        assert saved_files["all"].endswith("/rss/all.xml")

        # 验证文件内容
        rss_content = self.service.storage.read_rss("all")
        assert rss_content is not None
        assert "<rss version=\"2.0\">" in rss_content
        assert "<title>TrendRadar热点分析</title>" in rss_content
        assert "<title>测试标题1</title>" in rss_content

    def test_generate_and_save_rss_frequency_results(self):
        """测试使用频率结果生成并保存RSS"""
        # 创建模拟的频率结果
        frequency_results = {
            "keyword1": [
                {
                    "title": "测试标题1",
                    "url": "https://example.com/1",
                    "mobileUrl": "https://m.example.com/1",
                    "id": "test-source",
                    "rank": 1,
                    "count": 2
                }
            ]
        }
        id_to_name = {"test-source": "测试来源"}

        # 生成并保存RSS
        saved_files = self.service.generate_and_save_rss(frequency_results, id_to_name, use_raw_data=False)

        # 验证保存结果
        assert isinstance(saved_files, dict)
        assert len(saved_files) == 1
        assert "keyword1" in saved_files
        assert saved_files["keyword1"].endswith("/rss/keyword1.xml")

        # 验证文件内容
        rss_content = self.service.storage.read_rss("keyword1")
        assert rss_content is not None
        assert "<rss version=\"2.0\">" in rss_content
        assert "<title>TrendRadar热点分析</title>" in rss_content
        assert "<title>测试标题1</title>" in rss_content

    def test_get_rss_by_keyword(self):
        """测试获取特定关键词的RSS内容"""
        # 保存RSS文件
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )
        self.service.storage.save_rss_feed(feed, "test")

        # 获取RSS内容
        rss_content = self.service.get_rss_by_keyword("test")

        # 验证结果
        assert isinstance(rss_content, str)
        assert "<rss version=\"2.0\">" in rss_content
        assert "<title>测试Feed</title>" in rss_content

        # 测试获取不存在的RSS
        rss_content = self.service.get_rss_by_keyword("not_exists")
        assert rss_content is None

    def test_get_rss_statistics(self):
        """测试获取RSS统计信息"""
        # 初始状态
        stats = self.service.get_rss_statistics()
        assert isinstance(stats, dict)
        assert stats["total_subscriptions"] == 0
        assert stats["total_size"] == 0
        assert isinstance(stats["available_keywords"], list)
        assert len(stats["available_keywords"]) == 0
        assert isinstance(stats["last_update"], str)

        # 保存RSS文件后再次测试
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )
        self.service.storage.save_rss_feed(feed, "test")

        stats = self.service.get_rss_statistics()
        assert stats["total_subscriptions"] == 1
        assert stats["total_size"] > 0
        assert "test" in stats["available_keywords"]

    def test_get_rss_history(self):
        """测试获取RSS历史记录"""
        # 保存RSS文件
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )
        self.service.storage.save_rss_feed(feed, "test")

        # 获取历史记录
        history = self.service.get_rss_history("test")

        # 验证结果
        assert isinstance(history, list)
        assert len(history) == 1
        assert isinstance(history[0], dict)
        assert "filename" in history[0]
        assert "path" in history[0]
        assert "size" in history[0]
        assert "modified_time" in history[0]
        assert history[0]["filename"] == "test.xml"

        # 测试获取不存在的RSS历史记录
        history = self.service.get_rss_history("not_exists")
        assert isinstance(history, list)
        assert len(history) == 0

    def test_validate_rss_content(self):
        """测试验证RSS内容"""
        # 生成有效的RSS内容
        feed = RSSFeed(
            title="测试Feed",
            link="https://example.com/feed",
            description="测试Feed描述",
            pub_date=datetime.now()
        )
        valid_rss = self.service.storage.generator.generate_rss(feed)

        # 验证有效RSS
        is_valid = self.service.validate_rss_content(valid_rss)
        assert is_valid is True

        # 验证无效RSS
        invalid_rss = '<rss version=\"2.0\"><channel><title>Invalid</title></rss>'
        is_valid = self.service.validate_rss_content(invalid_rss)
        assert is_valid is False
