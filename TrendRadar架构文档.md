# TrendRadar 架构文档

## 目录
- [项目概述](#项目概述)
- [核心架构](#核心架构)
- [目录结构](#目录结构)
- [技术栈](#技术栈)
- [核心模块](#核心模块)
- [数据流详解](#数据流详解)
- [三种推送模式](#三种推送模式)
- [部署方式](#部署方式)
- [关键算法](#关键算法)
- [配置说明](#配置说明)

---

## 项目概述

TrendRadar 是一个智能新闻聚合和监控系统,通过关键词匹配自动追踪热搜趋势,支持多渠道推送通知。项目集成了 MCP (Model Context Protocol) 服务器,可以作为 AI 工具被 Claude 等模型调用。

### 核心特性

- **多平台聚合**: 支持 40+ 热搜平台(微博、百度、知乎、抖音等)
- **智能过滤**: 支持复杂关键词匹配、必须词、过滤词组合
- **三种推送模式**: daily(日报)、current(实时榜单)、incremental(增量监控)
- **多渠道通知**: 飞书、钉钉、企业微信、Telegram、Email、Ntfy、Bark、Slack
- **MCP集成**: 13个 AI 工具,支持自然语言查询和趋势分析
- **自动化部署**: GitHub Actions + Docker 双模式

---

## 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         TrendRadar 架构                          │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   配置加载层     │
                    │ config.yaml     │
                    │ frequency_words │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼──────┐  ┌─────▼─────┐  ┌──────▼───────┐
    │  主爬虫程序   │  │ MCP服务器  │  │  自动化调度   │
    │   main.py    │  │  server.py │  │ GitHub/Docker│
    └───────┬──────┘  └─────┬─────┘  └──────┬───────┘
            │                │                │
            │      ┌─────────┴────────┐       │
            │      │                  │       │
    ┌───────▼──────▼─────┐   ┌────────▼───────▼──┐
    │   NewsNow API      │   │   定时触发器        │
    │ (40+平台数据源)     │   │ cron/workflow      │
    └──────────┬──────────┘   └────────────────────┘
               │
    ┌──────────▼──────────┐
    │   JSON 数据解析      │
    │  title/url/rank     │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   关键词匹配过滤     │
    │ 必须词+普通词+过滤词 │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   权重计算排序       │
    │ 排名+频次+热度      │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   数据持久化         │
    │  output/txt/html    │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   推送窗口检查       │
    │  时间范围+每日一次   │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   多渠道推送         │
    │ 8种通知渠道+批次发送 │
    └─────────────────────┘

                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼─────┐    ┌────────▼────────┐
│  用户接收通知 │    │  MCP客户端调用   │
│ 飞书/钉钉/邮件│    │ Claude Desktop  │
└──────────────┘    └─────────────────┘
```

---

## 目录结构

```
TrendRadar/
├── main.py                        # 主爬虫程序 (4920行)
├── config/                        # 配置文件目录
│   ├── config.yaml               # 主配置 (平台/推送/模式)
│   └── frequency_words.txt       # 关键词配置
│
├── mcp_server/                    # MCP服务器模块
│   ├── server.py                 # FastMCP 2.0 服务器入口 (781行)
│   ├── services/                 # 核心服务层
│   │   ├── data_service.py       # 数据访问服务
│   │   ├── parser_service.py     # 文件解析服务
│   │   └── cache_service.py      # 缓存管理 (15分钟TTL)
│   ├── tools/                    # MCP工具实现
│   │   ├── data_query.py         # 数据查询工具
│   │   ├── analytics.py          # 趋势分析工具
│   │   ├── search_tools.py       # 智能搜索工具
│   │   ├── config_mgmt.py        # 配置管理工具
│   │   └── system.py             # 系统管理工具
│   └── utils/                    # 工具类
│       ├── date_parser.py        # 自然语言日期解析
│       ├── errors.py             # 错误定义
│       └── validators.py         # 数据验证器
│
├── output/                        # 数据输出目录
│   ├── YYYY年MM月DD日/            # 按日期组织
│   │   ├── txt/                  # 原始数据 (HH时MM分.txt)
│   │   └── html/                 # HTML报告
│   ├── .push_records/            # 推送记录 (隐藏目录)
│   └── index.html                # 最新报告链接
│
├── docker/                        # Docker部署配置
│   ├── Dockerfile                # 镜像构建文件
│   ├── docker-compose.yml        # 容器编排配置
│   ├── entrypoint.sh             # 启动脚本
│   ├── manage.py                 # 管理脚本
│   └── .env.example              # 环境变量模板
│
├── .github/workflows/             # GitHub Actions自动化
│   ├── crawler.yml               # 定时爬虫 (每2小时)
│   └── docker.yml                # Docker镜像构建
│
├── requirements.txt               # Python依赖
├── pyproject.toml                # 项目打包配置
└── README.md                     # 项目文档
```

---

## 技术栈

### 核心依赖

```python
requests>=2.32.5          # HTTP请求库,调用NewsNow API
pytz>=2025.2              # 时区处理 (Asia/Shanghai)
PyYAML>=6.0.3             # YAML配置文件解析
fastmcp>=2.12.0           # MCP服务器框架
websockets>=13.0          # WebSocket支持 (MCP通信)
```

### 运行环境

- **Python**: 3.10+
- **包管理器**: uv (现代化Python包管理)
- **数据源**: NewsNow API (https://newsnow.busiyi.world)
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

### 通知渠道

- 飞书 (Feishu Webhook)
- 钉钉 (DingTalk Webhook)
- 企业微信 (WeCom Webhook)
- Telegram (Bot API)
- Email (SMTP)
- Ntfy (Push Service)
- Bark (iOS Push)
- Slack (Incoming Webhook)

---

## 核心模块

### 1. 主爬虫程序 (main.py)

#### NewsAnalyzer - 新闻分析器

核心类,协调整个爬取、分析、推送流程。

**关键方法**:
- `run()`: 主执行流程
- `crawl_and_save()`: 爬取并保存数据
- `count_word_frequency()`: 关键词匹配和统计
- `generate_html_report()`: 生成可视化报告
- `send_to_notifications()`: 多渠道推送

**文件位置**: main.py:3859

#### DataFetcher - 数据获取器

负责从 NewsNow API 抓取数据。

**关键方法**:
- `fetch_data(platform_id)`: 请求单个平台数据
- `crawl_websites(platforms)`: 批量爬取多个平台

**文件位置**: main.py:507

#### PushRecordManager - 推送记录管理

实现推送窗口控制和去重。

**关键方法**:
- `is_in_time_range()`: 检查当前时间是否在推送窗口内
- `has_pushed_today()`: 检查今天是否已推送
- `record_push()`: 记录推送事件

**文件位置**: main.py:4666

### 2. MCP服务器 (mcp_server/server.py)

基于 FastMCP 2.0 框架,提供 13 个 AI 工具。

#### 核心工具

1. **resolve_date_range** - 日期解析
   - 输入: "本周", "最近7天", "2025-11-20"
   - 输出: {"start": "2025-11-18", "end": "2025-11-26"}

2. **search_news** - 统一搜索
   - 支持模式: keyword(关键词) / semantic(语义) / regex(正则)
   - 参数: query, date_range, platforms, limit, sort_by

3. **analyze_topic_trend** - 趋势分析
   - 输入: 话题关键词 + 日期范围
   - 输出: 每日出现次数、平台分布、热度变化

4. **get_latest_news** - 最新新闻
   - 缓存: 15分钟 (TTL)
   - 返回: 所有平台最新数据

**文件位置**: mcp_server/server.py

#### 服务层架构

- **DataService** (services/data_service.py): 数据访问服务,读取output目录
- **CacheService** (services/cache_service.py): 内存缓存,15分钟过期
- **ParserService** (services/parser_service.py): 文件解析服务

---

## 数据流详解

### 1. 数据获取流程

```
[配置加载]
    ↓
    load_config() → 读取 config.yaml
    ↓
    合并环境变量 (GitHub Secrets)
    ↓
    生成全局 CONFIG

[平台列表准备]
    ↓
    读取 CONFIG["PLATFORMS"]
    ↓
    构建 platform_id → name 映射

[数据爬取]
    ↓
    遍历每个平台ID
    ↓
    fetch_data(platform_id)
    ↓
    请求 NewsNow API
    ├─ URL: /api/s?id={id}&latest
    ├─ Headers: User-Agent, Accept
    └─ Proxy: 根据配置决定
    ↓
    返回 JSON: {"status": "success", "items": [...]}

[数据解析]
    ↓
    提取每条新闻:
    ├─ title: 标题
    ├─ url: PC链接
    ├─ mobileUrl: 移动链接
    └─ rank: 排名 (基于索引)
    ↓
    构建数据结构:
    results[platform_id][title] = {
        "ranks": [index],
        "url": url,
        "mobileUrl": mobileUrl
    }
```

### 2. 关键词匹配流程

```
[加载关键词配置]
    ↓
    load_frequency_words()
    ↓
    读取 config/frequency_words.txt
    ↓
    解析词组 (空行分组):
    word_groups = [
        {
            "required": [...],     # 必须词
            "normal": [...],       # 普通词
            "group_key": "组合关键词"
        }
    ]
    ↓
    提取过滤词 (!前缀)

[标题匹配]
    ↓
    遍历所有新闻标题
    ↓
    对每个词组调用 matches_word_groups():
        1. 检查过滤词 → 如包含则排除
        2. 检查必须词 → 必须全部包含
        3. 检查普通词 → 至少包含一个
    ↓
    匹配成功 → 进入统计

[词频统计]
    ↓
    count_word_frequency()
    ↓
    按词组分类统计
    ↓
    计算新闻权重:
    weight = rank_score × 0.6 + frequency_score × 0.3 + hotness_score × 0.1
    ↓
    排序:
    ├─ 先按配置位置或热点条数
    └─ 再按权重排序
    ↓
    限制每个关键词的新闻数量
```

### 3. 推送流程

```
[推送窗口检查]
    ↓
    PushRecordManager.is_in_time_range()
    ├─ 检查当前时间是否在窗口内
    └─ 检查今天是否已推送
    ↓
    不满足条件 → 跳过推送

[报告数据准备]
    ↓
    prepare_report_data()
    ├─ 整合统计结果
    ├─ 格式化新增新闻区域
    ├─ 添加失败平台信息
    └─ 添加版本更新提示

[多渠道内容渲染]
    ↓
    根据平台生成不同格式:
    ├─ 飞书: 卡片消息 (JSON) → 29KB/批
    ├─ 钉钉: Markdown → 20KB/批
    ├─ 企业微信: Markdown/Text → 4KB/批
    ├─ Telegram: HTML → 批次发送
    ├─ Email: HTML邮件 (MIME)
    ├─ Ntfy: Markdown
    ├─ Bark: URL编码
    └─ Slack: mrkdwn格式

[内容分批发送]
    ↓
    split_content_into_batches()
    ├─ 按字节大小切分
    ├─ 保留完整段落
    ├─ 添加分批标识 (第X/Y批)
    └─ 批次间延迟3秒
    ↓
    发送到各渠道
```

---

## 三种推送模式

### 模式对比

| 特性 | daily (日报) | current (实时榜单) | incremental (增量) |
|-----|-------------|-------------------|-------------------|
| **数据源** | 当日所有历史数据 | 当日所有历史数据 | 最新批次 vs 上一批次 |
| **推送时机** | 按时推送 | 按时推送 | 有新增才推送 |
| **显示内容** | 全天匹配新闻 | 最新批次匹配新闻 | 仅新增匹配新闻 |
| **新增区域** | 展示 | 展示 | 仅新增 |
| **统计信息** | 完整统计 | 完整统计 (历史) | 仅新增统计 |
| **适用场景** | 日报总结 | 实时热点追踪 | 避免重复信息 |

### 实现差异

#### daily 模式

```python
# 文件位置: main.py:3859
def run(self):
    # 1. 爬取最新数据
    results, id_to_name, failed_ids = self.crawl_and_save()

    # 2. 读取今天所有历史数据
    all_results = read_today_history(current_platform_ids)

    # 3. 统计完整词频
    frequency_results = count_word_frequency(all_results, ...)

    # 4. 生成HTML报告 (包含全天数据)
    generate_html_report(frequency_results, ...)

    # 5. 按时推送 (不管是否有新增)
    send_to_notifications(...)
```

#### current 模式

```python
# 文件位置: main.py:3859
def run(self):
    # 1. 爬取最新数据
    results, id_to_name, failed_ids = self.crawl_and_save()

    # 2. 读取今天所有历史数据 (用于统计信息)
    all_results = read_today_history(current_platform_ids)

    # 3. 从历史数据中筛选最新时间批次的新闻
    current_results = get_latest_batch_news(all_results)

    # 4. 使用完整统计信息 (first_time, last_time, count)
    frequency_results = count_word_frequency(
        current_results,
        all_results_for_stats=all_results,
        ...
    )

    # 5. 生成当前榜单报告 + 新增新闻区域
    generate_html_report(frequency_results, ...)

    # 6. 按时推送
    send_to_notifications(...)
```

#### incremental 模式

```python
# 文件位置: main.py:3859
def run(self):
    # 1. 爬取最新数据
    results, id_to_name, failed_ids = self.crawl_and_save()

    # 2. 检测新增标题 (对比上一批次)
    new_titles = detect_latest_new_titles(current_platform_ids)

    # 3. 如果第一次爬取: 所有新闻都算新增
    if is_first_crawl_today():
        new_titles = results

    # 4. 只有新增匹配的新闻时才处理
    if new_titles:
        frequency_results = count_word_frequency(new_titles, ...)
        generate_html_report(frequency_results, ...)
        send_to_notifications(...)
    else:
        print("没有新增新闻,跳过推送")
```

---

## 部署方式

### 1. GitHub Actions 部署 (推荐入门)

**优势**:
- 零成本 (免费配额)
- 零运维 (无需服务器)
- 自动化 (定时执行)

**配置文件**: `.github/workflows/crawler.yml`

```yaml
on:
  schedule:
    - cron: "0 */2 * * *"  # 每2小时执行 (UTC时间)
  workflow_dispatch:        # 支持手动触发

jobs:
  crawl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
          # ... 其他Webhook配置
      - run: |
          git config user.name "github-actions[bot]"
          git add output/
          git commit -m "Auto update by GitHub Actions"
          git push
```

**限制**:
- 最小间隔30分钟 (建议)
- 执行时间不稳定 (±5分钟)
- 每月2000分钟配额

### 2. Docker 部署 (推荐生产)

**优势**:
- 高频采集 (最小1分钟)
- 执行稳定 (精准控制)
- 数据本地化 (隐私安全)

**docker-compose.yml**:

```yaml
services:
  trend-radar:
    image: wantcat/trendradar:latest
    container_name: trend-radar
    restart: unless-stopped
    volumes:
      - ./config:/app/config:ro    # 配置只读
      - ./output:/app/output        # 输出可写
    environment:
      - TZ=Asia/Shanghai
      - CRON_SCHEDULE=*/5 * * * *   # 每5分钟
      - RUN_MODE=cron               # 运行模式
      - IMMEDIATE_RUN=true          # 立即执行一次
      - REPORT_MODE=incremental     # 增量模式
      - FEISHU_WEBHOOK_URL=${FEISHU_WEBHOOK_URL}
      # ... 其他环境变量
```

**启动命令**:

```bash
# 1. 准备配置
vim config/config.yaml
vim config/frequency_words.txt

# 2. 配置环境变量
cp docker/.env.example docker/.env
vim docker/.env

# 3. 启动容器
docker-compose -f docker/docker-compose.yml up -d

# 4. 查看日志
docker logs -f trend-radar
```

### 3. 本地运行 (调试推荐)

```bash
# 安装依赖
pip install -r requirements.txt

# 运行主程序
python main.py

# 运行MCP服务器
python -m mcp_server.server --transport stdio
```

---

## 关键算法

### 1. 新闻权重计算

**文件**: main.py:2985

```python
def calculate_news_weight(
    title_data: Dict,
    rank_weight: float = 0.6,
    frequency_weight: float = 0.3,
    hotness_weight: float = 0.1
) -> float:
    """
    综合权重 = 排名分 × 0.6 + 频次分 × 0.3 + 热度分 × 0.1

    排名分: max(0, 100 - avg_rank)
    频次分: min(100, count × 10)
    热度分: 50 (预留接口)
    """
    ranks = title_data.get("ranks", [])
    count = title_data.get("count", 1)

    # 排名分
    avg_rank = sum(ranks) / len(ranks) if ranks else 0
    rank_score = max(0, 100 - avg_rank)

    # 频次分
    frequency_score = min(100, count * 10)

    # 热度分
    hotness_score = 50

    # 加权求和
    weight = (
        rank_score * rank_weight +
        frequency_score * frequency_weight +
        hotness_score * hotness_weight
    )

    return weight
```

### 2. 增量检测算法

**文件**: main.py:3698

```python
def detect_latest_new_titles(current_platform_ids: Optional[List[str]] = None) -> Dict:
    """
    检测当日最新批次的新增标题

    算法:
    1. 读取今天所有txt文件 (按时间排序)
    2. 如果只有1个文件 → 全部都是新增
    3. 如果有多个文件:
       - 读取最新文件的标题集合
       - 读取倒数第二个文件的标题集合
       - 计算差集: new_titles = latest - previous
    """
    txt_files = sorted(txt_folder.glob("*.txt"))

    if len(txt_files) < 2:
        # 第一次爬取,所有新闻都是新增
        return parse_file_titles(txt_files[0])

    # 读取最新和上一次的文件
    latest_titles = parse_file_titles(txt_files[-1])
    previous_titles = parse_file_titles(txt_files[-2])

    # 计算新增标题
    new_titles = {}
    for platform_id, titles in latest_titles.items():
        previous_set = set(previous_titles.get(platform_id, {}).keys())
        new_set = set(titles.keys()) - previous_set

        if new_set:
            new_titles[platform_id] = {
                title: titles[title] for title in new_set
            }

    return new_titles
```

### 3. 关键词匹配算法

**文件**: main.py:1024

```python
def matches_word_groups(title: str, word_groups: List[Dict]) -> Optional[str]:
    """
    关键词匹配逻辑

    规则:
    1. 检查过滤词 (!前缀) → 如包含则排除
    2. 检查必须词 → 必须全部包含
    3. 检查普通词 → 至少包含一个

    返回: 匹配成功返回group_key,否则返回None
    """
    title_lower = title.lower()

    for group in word_groups:
        # 1. 检查过滤词
        if any(filter_word in title_lower for filter_word in group["filter"]):
            continue

        # 2. 检查必须词
        required_words = group["required"]
        if required_words:
            if not all(word in title_lower for word in required_words):
                continue

        # 3. 检查普通词
        normal_words = group["normal"]
        if not any(word in title_lower for word in normal_words):
            continue

        # 全部匹配成功
        return group["group_key"]

    return None
```

### 4. 自然语言日期解析

**文件**: mcp_server/utils/date_parser.py

```python
class DateParser:
    def parse_date_range(self, date_str: str) -> Dict[str, str]:
        """
        支持格式:
        - "今天", "昨天", "前天"
        - "本周", "上周", "本月", "上月"
        - "最近7天", "最近30天"
        - "2025-11-20"
        - "2025-11-20 to 2025-11-26"

        返回: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
        """
```

---

## 配置说明

### 主配置文件 (config/config.yaml)

```yaml
# 应用配置
app:
  version_check_url: "https://api.github.com/repos/HuYuanlong/TrendRadar/releases/latest"
  show_version_update: true

# 爬虫配置
crawler:
  request_interval: 1000        # 请求间隔 (毫秒)
  enable_crawler: true          # 是否启用爬取
  use_proxy: false              # 是否使用代理
  default_proxy: "http://127.0.0.1:7890"

# 报告配置
report:
  mode: "daily"                 # 推送模式: daily|current|incremental
  rank_threshold: 5             # 排名高亮阈值
  sort_by_position_first: false # 排序优先级
  max_news_per_keyword: 0       # 每个关键词最大显示数量 (0=不限制)

# 通知配置
notification:
  enable_notification: true     # 是否启用通知
  message_batch_size: 4000      # 通用批次大小 (字节)
  dingtalk_batch_size: 20000    # 钉钉批次
  feishu_batch_size: 29000      # 飞书批次
  bark_batch_size: 3600         # Bark批次
  slack_batch_size: 4000        # Slack批次
  batch_send_interval: 3        # 批次间隔 (秒)

  # 推送时间窗口 (可选)
  push_window:
    enabled: false              # 是否启用
    time_range:
      start: "20:00"
      end: "22:00"
    once_per_day: true          # 每天只推送一次
    push_record_retention_days: 7

  # Webhook配置 (建议使用环境变量)
  webhooks:
    feishu_url: ""
    dingtalk_url: ""
    wework_url: ""
    telegram_bot_token: ""
    telegram_chat_id: ""
    # ... 其他渠道配置

# 权重配置
weight:
  rank_weight: 0.6              # 排名权重
  frequency_weight: 0.3         # 频次权重
  hotness_weight: 0.1           # 热度权重

# 平台配置 (支持40+平台)
platforms:
  - id: "toutiao"
    name: "今日头条"
  - id: "baidu"
    name: "百度热搜"
  - id: "weibo"
    name: "微博"
  # ... 其他平台
```

### 关键词配置 (config/frequency_words.txt)

```
# 词组1: AI相关 (空行分组)
DeepSeek
梁文锋

# 词组2: 科技公司
华为
鸿蒙

# 词组3: 通用AI (支持过滤词)
ai
!gai          # !前缀表示过滤,排除误匹配
人工智能
大模型

# 匹配规则:
# 1. 同组内的词用OR关系 (任一匹配即可)
# 2. 不同组之间独立统计
# 3. !前缀表示排除词
```

---

## 数据格式

### TXT 文件格式

```
toutiao | 今日头条
1. 金灿荣:日本盟友不表态已说明问题 [URL:https://...]
2. 33岁驻村女干部去世 系清华硕士 [URL:https://...]

baidu | 百度热搜
1. 曝高市早苗花8千万日元仍败给石破茂 [URL:https://...]

==== 以下ID请求失败 ====
失败的平台ID列表 (如有)
```

### 推送记录格式

```json
{
  "pushed": true,
  "push_time": "2025-12-02 20:05:30",
  "report_type": "当日汇总"
}
```

---

## 性能指标

| 指标 | 数值 |
|-----|------|
| 总代码行数 | ~5700行 |
| 支持平台数 | 40+ |
| 通知渠道数 | 8种 |
| MCP工具数 | 13个 |
| 缓存TTL | 15分钟 |
| API请求间隔 | 1秒 |
| Docker镜像大小 | ~200MB |

---

## 扩展建议

### 1. 新增平台

编辑 `config/config.yaml`:

```yaml
platforms:
  - id: "新平台ID"
    name: "新平台名称"
```

### 2. 新增通知渠道

1. 在 `main.py` 中实现 `send_to_xxx()` 函数
2. 在 `send_to_notifications()` 中调用
3. 在 `config.yaml` 中添加配置

### 3. 新增MCP工具

```python
# mcp_server/server.py
@mcp.tool
async def new_tool(param1: str, param2: int) -> str:
    """工具描述"""
    # 实现逻辑
    return result
```

### 4. 自定义权重算法

修改 `calculate_news_weight()` 函数,调整权重参数:

```python
weight = (
    rank_score * 0.5 +      # 降低排名权重
    frequency_score * 0.4 + # 提高频次权重
    hotness_score * 0.1
)
```

---

## 常见问题

### Q1: 如何修改爬取频率?

**GitHub Actions**:
编辑 `.github/workflows/crawler.yml`:
```yaml
schedule:
  - cron: "0 */1 * * *"  # 改为每1小时
```

**Docker**:
编辑 `docker-compose.yml`:
```yaml
environment:
  - CRON_SCHEDULE=*/10 * * * *  # 改为每10分钟
```

### Q2: 如何只监控特定平台?

编辑 `config/config.yaml`,只保留需要的平台:
```yaml
platforms:
  - id: "weibo"
    name: "微博"
  - id: "zhihu"
    name: "知乎"
```

### Q3: 如何避免夜间推送?

启用推送窗口:
```yaml
notification:
  push_window:
    enabled: true
    time_range:
      start: "09:00"
      end: "21:00"
    once_per_day: false
```

### Q4: 如何配置MCP服务器?

```bash
# Claude Desktop配置路径:
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json

{
  "mcpServers": {
    "trendradar": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/TrendRadar"
    }
  }
}
```

---

## 项目统计

```
Language           Files    Lines    Code    Comments    Blank
─────────────────────────────────────────────────────────────
Python                13     5701    4892         312      497
YAML                   3      356     321          12       23
Markdown               2      892       0         727      165
Dockerfile             1       43      29           9        5
Shell                  2      126      85          21       20
─────────────────────────────────────────────────────────────
Total                 21     7118    5327        1081      710
```

---

## 总结

TrendRadar 的核心优势在于:
- **模块化设计**: 易于扩展和维护
- **灵活配置**: 支持多种推送模式和渠道
- **智能过滤**: 复杂关键词匹配系统
- **AI集成**: MCP服务器提供13个AI工具
- **多种部署**: GitHub Actions / Docker / 本地运行

通过原始架构 **NewNow API → JSON解析 → 过滤 → 推送** 的简洁设计,结合现代化的技术栈和完善的功能模块,TrendRadar 能够高效地帮助用户追踪热点趋势。

---

**文档版本**: v1.0
**最后更新**: 2025-12-02
**维护者**: TrendRadar Team
