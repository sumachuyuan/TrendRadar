import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from rss.generator import RSSGenerator
from rss.models import RSSFeed, RSSItem


class RSSStorage:
    """RSS数据持久化存储类"""

    def __init__(self, base_dir: str = "output/rss"):
        self.base_dir = Path(base_dir)
        self.generator = RSSGenerator()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """确保存储目录存在"""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_guid(title: str, link: str, pub_date: datetime) -> str:
        """生成唯一标识"""
        unique_str = f"{title}{link}{pub_date.isoformat()}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def _get_file_path(self, keyword: str, date: Optional[datetime] = None) -> Path:
        """获取RSS文件路径"""
        if date is None:
            date = datetime.now()
        filename = f"{keyword}.xml"
        return self.base_dir / filename

    def _read_existing_rss(self, keyword: str) -> Optional[RSSFeed]:
        """读取已存在的RSS文件"""
        file_path = self._get_file_path(keyword)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 解析XML并转换为RSSFeed对象
            # 这里简化处理，实际应该实现完整的XML解析
            # 目前返回None，后续完善
            return None
        except Exception as e:
            print(f"读取RSS文件失败: {e}")
            return None

    def _get_existing_guids(self, feed: Optional[RSSFeed]) -> Set[str]:
        """获取已存在的GUID集合"""
        if not feed:
            return set()
        return {item.guid for item in feed.items}

    def save_rss_feed(self, feed: RSSFeed, keyword: str) -> Path:
        """保存RSS Feed到文件，支持增量更新"""
        # 生成RSS内容
        rss_content = self.generator.generate_rss(feed)
        
        # 获取文件路径
        file_path = self._get_file_path(keyword)
        
        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        return file_path

    def save_rss_by_keyword(self, feed: RSSFeed, keyword: str) -> Path:
        """根据关键词保存RSS，实现增量更新"""
        # 生成关键词相关的RSS内容
        rss_content = self.generator.generate_rss_by_keyword(feed, keyword)
        
        # 获取文件路径
        file_path = self._get_file_path(keyword)
        
        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        return file_path

    def save_multiple_feeds(self, feed: RSSFeed) -> Dict[str, Path]:
        """保存多个关键词的RSS"""
        # 提取所有关键词
        all_keywords = set()
        for item in feed.items:
            all_keywords.update(item.keywords)
        
        # 保存每个关键词的RSS
        saved_files = {}
        for keyword in all_keywords:
            file_path = self.save_rss_by_keyword(feed, keyword)
            saved_files[keyword] = file_path
        
        # 保存完整的RSS
        full_file_path = self.save_rss_feed(feed, "all")
        saved_files["all"] = full_file_path
        
        return saved_files

    def read_rss(self, keyword: str) -> Optional[str]:
        """读取指定关键词的RSS内容"""
        file_path = self._get_file_path(keyword)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"读取RSS内容失败: {e}")
            return None

    def list_available_keywords(self) -> List[str]:
        """列出所有可用的RSS关键词"""
        keywords = []
        for file_path in self.base_dir.iterdir():
            if file_path.suffix == ".xml":
                keyword = file_path.stem
                keywords.append(keyword)
        return keywords

    def delete_old_rss(self, days: int = 30) -> int:
        """删除指定天数前的RSS文件"""
        deleted_count = 0
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for file_path in self.base_dir.iterdir():
            if file_path.suffix == ".xml":
                mtime = file_path.stat().st_mtime
                if mtime < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
        
        return deleted_count

    def get_rss_history(self, keyword: str) -> List[Path]:
        """获取RSS历史记录"""
        # 目前只返回当前文件，后续可以扩展支持历史版本
        file_path = self._get_file_path(keyword)
        if file_path.exists():
            return [file_path]
        return []

    def is_duplicate(self, item: RSSItem, existing_guids: Set[str]) -> bool:
        """检查RSS条目是否重复"""
        return item.guid in existing_guids

    def add_item_to_feed(self, feed: RSSFeed, item: RSSItem, existing_guids: Set[str]) -> bool:
        """添加RSS条目到Feed，避免重复"""
        if not self.is_duplicate(item, existing_guids):
            feed.add_item(item)
            return True
        return False
