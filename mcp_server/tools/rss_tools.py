"""
RSS工具

实现RSS相关的MCP工具。
"""

import json
from typing import Dict, List, Optional

from rss.service import RSSService
from ..utils.errors import MCPError


class RssTools:
    """RSS工具类"""

    def __init__(self, project_root: str = None):
        """
        初始化RSS工具

        Args:
            project_root: 项目根目录
        """
        self.rss_service = RSSService()

    def get_rss_subscriptions(self) -> Dict:
        """
        获取所有RSS订阅列表

        Returns:
            RSS订阅列表字典

        Example:
            >>> tools = RssTools()
            >>> result = tools.get_rss_subscriptions()
            >>> print(result['subscriptions'][0]['title'])
            TrendRadar - AI
        """
        try:
            subscriptions = self.rss_service.get_rss_subscriptions()
            
            return {
                "subscriptions": subscriptions,
                "total": len(subscriptions),
                "success": True
            }

        except MCPError as e:
            return {
                "success": False,
                "error": e.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }

    def get_rss_by_keyword(self, keyword: str) -> Dict:
        """
        获取特定关键词的RSS内容

        Args:
            keyword: 关键词，如 'AI' 或 'all'

        Returns:
            RSS内容字典

        Example:
            >>> tools = RssTools()
            >>> result = tools.get_rss_by_keyword('AI')
            >>> print(result['success'])
            True
        """
        try:
            # 参数验证
            if not keyword:
                raise MCPError("KEYWORD_REQUIRED", "关键词不能为空")

            # 获取RSS内容
            rss_content = self.rss_service.get_rss_by_keyword(keyword)
            
            if rss_content is None:
                raise MCPError("RSS_NOT_FOUND", f"未找到关键词 {keyword} 的RSS内容")
            
            return {
                "keyword": keyword,
                "rss_content": rss_content,
                "success": True
            }

        except MCPError as e:
            return {
                "success": False,
                "error": e.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }

    def get_rss_statistics(self) -> Dict:
        """
        获取RSS统计信息

        Returns:
            RSS统计信息字典

        Example:
            >>> tools = RssTools()
            >>> result = tools.get_rss_statistics()
            >>> print(result['total_subscriptions'])
            10
        """
        try:
            statistics = self.rss_service.get_rss_statistics()
            
            return {
                **statistics,
                "success": True
            }

        except MCPError as e:
            return {
                "success": False,
                "error": e.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }

    def get_rss_history(self, keyword: str) -> Dict:
        """
        获取RSS历史记录

        Args:
            keyword: 关键词，如 'AI' 或 'all'

        Returns:
            RSS历史记录字典

        Example:
            >>> tools = RssTools()
            >>> result = tools.get_rss_history('AI')
            >>> print(result['history'][0]['filename'])
            AI.txt
        """
        try:
            # 参数验证
            if not keyword:
                raise MCPError("KEYWORD_REQUIRED", "关键词不能为空")

            # 获取RSS历史记录
            history = self.rss_service.get_rss_history(keyword)
            
            return {
                "keyword": keyword,
                "history": history,
                "total": len(history),
                "success": True
            }

        except MCPError as e:
            return {
                "success": False,
                "error": e.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
