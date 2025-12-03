from datetime import datetime
from typing import Dict, List, Optional

from rss.generator import RSSGenerator
from rss.models import RSSFeed, RSSItem
from rss.storage import RSSStorage


class RSSService:
    """RSS服务接口类"""

    def __init__(self):
        self.generator = RSSGenerator()
        self.storage = RSSStorage()
        self.base_url = "https://trendradar.example.com"

    def generate_rss_feed(self, frequency_results: Dict, id_to_name: Dict) -> RSSFeed:
        """根据频率结果生成RSS Feed"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="TrendRadar热点分析",
            link=self.base_url,
            description="TrendRadar智能新闻聚合和监控系统生成的RSS Feed",
            pub_date=datetime.now()
        )

        # 遍历频率结果，生成RSS条目
        for group_key, items in frequency_results.items():
            for item_data in items:
                title = item_data.get("title", "")
                link = item_data.get("url", "")
                mobile_link = item_data.get("mobileUrl", "")
                source_id = item_data.get("id", "")
                source_name = id_to_name.get(source_id, source_id)
                rank = item_data.get("rank", 0)
                pub_date = datetime.now()  # 使用当前时间作为发布时间

                # 生成描述
                description = f"来源: {source_name} | 排名: {rank}"
                if item_data.get("count", 0) > 1:
                    description += f" | 出现次数: {item_data['count']}"

                # 生成唯一标识
                guid = self.storage._generate_guid(title, link, pub_date)

                # 创建RSS条目
                rss_item = RSSItem(
                    title=title,
                    link=link,
                    description=description,
                    pub_date=pub_date,
                    guid=guid,
                    source_id=source_id,
                    source_name=source_name,
                    rank=rank,
                    mobile_link=mobile_link,
                    keywords=[group_key]
                )

                # 添加到Feed
                feed.add_item(rss_item)

        # 按日期排序
        feed.sort_items_by_date()

        return feed

    def generate_rss_from_raw_data(self, results: Dict, id_to_name: Dict) -> RSSFeed:
        """根据原始抓取数据生成RSS Feed（包含所有新闻，不进行关键字过滤）"""
        # 创建RSS Feed
        feed = RSSFeed(
            title="TrendRadar热点分析",
            link=self.base_url,
            description="TrendRadar智能新闻聚合和监控系统生成的RSS Feed（包含全部内容）",
            pub_date=datetime.now()
        )

        # 遍历原始数据，生成RSS条目
        for source_id, title_data in results.items():
            source_name = id_to_name.get(source_id, source_id)
            
            for title, info in title_data.items():
                # 提取新闻信息
                cleaned_title = title
                if isinstance(info, dict):
                    ranks = info.get("ranks", [])
                    url = info.get("url", "")
                    mobile_url = info.get("mobileUrl", "")
                else:
                    ranks = info if isinstance(info, list) else []
                    url = ""
                    mobile_url = ""

                rank = ranks[0] if ranks else 1
                pub_date = datetime.now()

                # 生成描述
                description = f"来源: {source_name} | 排名: {rank}"

                # 生成唯一标识
                guid = self.storage._generate_guid(cleaned_title, url, pub_date)

                # 创建RSS条目
                rss_item = RSSItem(
                    title=cleaned_title,
                    link=url,
                    description=description,
                    pub_date=pub_date,
                    guid=guid,
                    source_id=source_id,
                    source_name=source_name,
                    rank=rank,
                    mobile_link=mobile_url,
                    keywords=["all"]
                )

                # 添加到Feed
                feed.add_item(rss_item)

        # 按日期排序
        feed.sort_items_by_date()

        return feed

    def get_rss_subscriptions(self) -> List[Dict]:
        """获取所有RSS订阅列表"""
        keywords = self.storage.list_available_keywords()
        subscriptions = []
        
        for keyword in keywords:
            subscriptions.append({
                "keyword": keyword,
                "title": f"TrendRadar - {keyword}",
                "link": f"{self.base_url}/rss/{keyword}.xml",
                "description": f"TrendRadar热点分析 - {keyword}相关内容"
            })
        
        return subscriptions

    def get_rss_by_keyword(self, keyword: str) -> Optional[str]:
        """获取特定关键词的RSS内容"""
        return self.storage.read_rss(keyword)

    def generate_and_save_rss(self, data: Dict, id_to_name: Dict, use_raw_data: bool = False) -> Dict[str, str]:
        """生成并保存RSS内容，支持原始数据模式
        
        Args:
            data: 输入数据，可以是原始抓取数据或频率结果
            id_to_name: 平台ID到名称的映射
            use_raw_data: 是否使用原始数据模式，不进行关键字过滤
        
        Returns:
            保存的文件路径字典
        """
        if use_raw_data:
            # 从原始数据生成RSS
            feed = self.generate_rss_from_raw_data(data, id_to_name)
            # 保存RSS（只保存all.xml，因为是全部内容）
            saved_files = {}
            file_path = self.storage.save_rss_feed(feed, "all")
            saved_files["all"] = str(file_path)
            return saved_files
        else:
            # 原有逻辑，从频率结果生成RSS
            feed = self.generate_rss_feed(data, id_to_name)
            saved_files = self.storage.save_multiple_feeds(feed)
            # 返回保存结果
            result = {}
            for keyword, file_path in saved_files.items():
                result[keyword] = str(file_path)
            return result

    def get_rss_history(self, keyword: str) -> List[Dict]:
        """获取RSS历史记录"""
        history_files = self.storage.get_rss_history(keyword)
        history = []
        
        for file_path in history_files:
            history.append({
                "filename": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        
        return history

    def validate_rss_content(self, rss_content: str) -> bool:
        """验证RSS内容格式是否正确"""
        return self.generator.validate_rss(rss_content)

    def get_rss_statistics(self) -> Dict:
        """获取RSS统计信息"""
        keywords = self.storage.list_available_keywords()
        
        total_files = len(keywords)
        total_size = 0
        
        for keyword in keywords:
            file_path = self.storage._get_file_path(keyword)
            if file_path.exists():
                total_size += file_path.stat().st_size
        
        return {
            "total_subscriptions": total_files,
            "total_size": total_size,
            "available_keywords": keywords,
            "last_update": datetime.now().isoformat()
        }

    def cleanup_old_rss(self, days: int = 30) -> Dict:
        """清理旧的RSS文件"""
        deleted_count = self.storage.delete_old_rss(days)
        
        return {
            "deleted_count": deleted_count,
            "cleanup_time": datetime.now().isoformat(),
            "retention_days": days
        }
