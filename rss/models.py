from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RSSItem:
    """RSS条目数据模型"""
    title: str                  # 新闻标题
    link: str                   # 新闻链接
    description: str            # 新闻描述
    pub_date: datetime          # 发布日期
    guid: str                   # 唯一标识
    source_id: Optional[str] = None  # 来源平台ID
    source_name: Optional[str] = None  # 来源平台名称
    rank: Optional[int] = None  # 排名
    mobile_link: Optional[str] = None  # 移动端链接
    keywords: List[str] = field(default_factory=list)  # 匹配的关键词


@dataclass
class RSSFeed:
    """RSS Feed数据模型"""
    title: str                  # Feed标题
    link: str                   # Feed链接
    description: str            # Feed描述
    pub_date: datetime          # 发布日期
    language: str = "zh-CN"      # 语言
    items: List[RSSItem] = field(default_factory=list)  # RSS条目列表
    generator: str = "TrendRadar RSS Generator"  # 生成器
    last_build_date: Optional[datetime] = None  # 最后更新日期

    def __post_init__(self):
        if self.last_build_date is None:
            self.last_build_date = self.pub_date

    def add_item(self, item: RSSItem) -> None:
        """添加RSS条目"""
        self.items.append(item)

    def get_items_by_keyword(self, keyword: str) -> List[RSSItem]:
        """根据关键词获取RSS条目"""
        return [item for item in self.items if keyword in item.keywords]

    def sort_items_by_date(self, reverse: bool = True) -> None:
        """按日期排序RSS条目"""
        self.items.sort(key=lambda x: x.pub_date, reverse=reverse)

    def limit_items(self, limit: int) -> None:
        """限制RSS条目数量"""
        self.items = self.items[:limit]
