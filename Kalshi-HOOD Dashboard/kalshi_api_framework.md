# Kalshi API 数据访问框架

## 概述

Kalshi 提供 REST API 用于访问预测市场数据。与 Polymarket 不同，Kalshi 是中心化平台，数据可通过官方 API 直接获取，**无需链上数据解析，也不存在 double counting 问题**。

---

## 1. API 基础信息

### 1.1 Base URL
```
https://api.elections.kalshi.com/trade-api/v2
```
> ⚠️ 注意：尽管 URL 包含 "elections"，但该 API 提供 **所有** Kalshi 市场的数据（包括经济、气候、科技、娱乐等类别）

### 1.2 认证方式

**公开端点（无需认证）：**
- GET /markets - 获取市场列表
- GET /markets/{ticker} - 获取单个市场
- GET /markets/trades - 获取交易历史
- GET /events - 获取事件列表

**私有端点（需要 API Key）：**
- Portfolio 相关操作
- 下单 / 撤单操作

### 1.3 认证 Headers（私有端点）
```
KALSHI-ACCESS-KEY: <your_api_key_id>
KALSHI-ACCESS-SIGNATURE: <cryptographic_signature>
KALSHI-ACCESS-TIMESTAMP: <timestamp_in_milliseconds>
```

签名算法：`HMAC-SHA256(timestamp + HTTP_method + path_without_query)`

---

## 2. 核心数据端点

### 2.1 获取市场列表 (GET /markets)

**用途**：批量获取市场数据，包括 volume 和 open interest

**请求示例**：
```bash
curl -X GET "https://api.elections.kalshi.com/trade-api/v2/markets?limit=100"
```

**响应结构**：
```json
{
  "markets": [
    {
      "ticker": "INXD-26FEB05-B6073",
      "event_ticker": "INXD-26FEB05",
      "title": "S&P 500 to close at or above 6,073?",
      "market_type": "binary",
      "status": "active",

      // ⭐ Volume 数据
      "volume": 12345,           // 总交易量（合约数）
      "volume_fp": "12345.00",   // 浮点格式
      "volume_24h": 567,         // 24小时交易量
      "volume_24h_fp": "567.00",

      // ⭐ Open Interest 数据
      "open_interest": 890,      // 未平仓合约数
      "open_interest_fp": "890.00",

      // 价格数据
      "yes_bid": 45,
      "yes_ask": 47,
      "no_bid": 53,
      "no_ask": 55,
      "last_price": 46,

      // 时间戳
      "open_time": "2026-02-05T00:00:00Z",
      "close_time": "2026-02-05T21:00:00Z",
      "expiration_time": "2026-02-06T00:00:00Z"
    }
  ],
  "cursor": "<pagination_cursor>"
}
```

**关键字段说明**：

| 字段 | 类型 | 含义 | HOOD 投资相关性 |
|-----|------|------|----------------|
| `volume` | integer | 累计交易合约数 | ⭐ 费用收入基数 ($0.02/合约) |
| `volume_24h` | integer | 24小时交易量 | ⭐ 日收入估算 |
| `open_interest` | integer | 未平仓合约 | 市场活跃度指标 |
| `yes_bid/ask` | integer | Yes 买卖价 (1-99 cents) | 流动性指标 |
| `status` | string | active/closed/settled | 过滤活跃市场 |

### 2.2 获取单个市场 (GET /markets/{ticker})

**用途**：获取特定市场的详细数据

**请求示例**：
```bash
curl -X GET "https://api.elections.kalshi.com/trade-api/v2/markets/INXD-26FEB05-B6073"
```

### 2.3 获取交易历史 (GET /markets/trades)

**用途**：获取所有市场或特定市场的交易记录

**请求参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| `ticker` | string | 过滤特定市场 |
| `min_ts` | timestamp | 开始时间 |
| `max_ts` | timestamp | 结束时间 |
| `limit` | integer | 每页数量 (1-1000, 默认100) |
| `cursor` | string | 分页游标 |

**请求示例**：
```bash
curl -X GET "https://api.elections.kalshi.com/trade-api/v2/markets/trades?limit=100&ticker=INXD-26FEB05-B6073"
```

**响应结构**：
```json
{
  "trades": [
    {
      "trade_id": "abc123",
      "ticker": "INXD-26FEB05-B6073",
      "count": 10,              // 合约数量
      "count_fp": "10.00",
      "yes_price": 46,          // Yes 成交价 (cents)
      "no_price": 54,           // No 成交价 (cents)
      "yes_price_dollars": "0.46",
      "no_price_dollars": "0.54",
      "taker_side": "yes",      // Taker 方向
      "created_time": "2026-02-05T14:30:00Z"
    }
  ],
  "cursor": "<next_page_cursor>"
}
```

### 2.4 获取事件 (GET /events)

**用途**：获取事件级别数据（一个事件可包含多个市场）

---

## 3. HOOD 投资分析框架

### 3.1 收入估算公式

```
Daily Revenue = Daily Volume (contracts) × $0.02

其中:
- $0.01 = Commission (给 Robinhood)
- $0.01 = Exchange Fee (给 Kalshi)
```

### 3.2 数据采集 Python 脚本

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

def get_all_markets(status="active"):
    """获取所有活跃市场的 volume 数据"""
    markets = []
    cursor = None

    while True:
        params = {"limit": 200, "status": status}
        if cursor:
            params["cursor"] = cursor

        response = requests.get(f"{BASE_URL}/markets", params=params)
        data = response.json()

        markets.extend(data.get("markets", []))
        cursor = data.get("cursor")

        if not cursor:
            break

    return markets

def calculate_daily_volume():
    """计算24小时交易量汇总"""
    markets = get_all_markets()

    total_volume_24h = sum(m.get("volume_24h", 0) for m in markets)
    total_open_interest = sum(m.get("open_interest", 0) for m in markets)

    return {
        "total_volume_24h": total_volume_24h,
        "total_open_interest": total_open_interest,
        "estimated_daily_revenue": total_volume_24h * 0.02,
        "market_count": len(markets),
        "timestamp": datetime.utcnow().isoformat()
    }

def get_historical_trades(ticker=None, days=7):
    """获取历史交易记录"""
    trades = []
    cursor = None

    min_ts = int((datetime.utcnow() - timedelta(days=days)).timestamp())

    while True:
        params = {"limit": 1000, "min_ts": min_ts}
        if cursor:
            params["cursor"] = cursor
        if ticker:
            params["ticker"] = ticker

        response = requests.get(f"{BASE_URL}/markets/trades", params=params)
        data = response.json()

        trades.extend(data.get("trades", []))
        cursor = data.get("cursor")

        if not cursor:
            break

    return trades

# 使用示例
if __name__ == "__main__":
    stats = calculate_daily_volume()
    print(f"24h Volume: {stats['total_volume_24h']:,} contracts")
    print(f"Open Interest: {stats['total_open_interest']:,} contracts")
    print(f"Est. Daily Revenue: ${stats['estimated_daily_revenue']:,.2f}")
```

### 3.3 与 Dune Dashboard 数据对比

| 数据源 | 优点 | 缺点 |
|-------|------|------|
| **Kalshi API** | 官方数据、实时、无 double counting | 需要自行聚合 |
| **Dune Dashboard** | 已聚合、跨平台对比 | Kalshi 数据为 Notional (已处理) |

---

## 4. 数据口径总结

### 4.1 Kalshi vs Polymarket 对比

| 指标 | Kalshi (API) | Polymarket (Dune) |
|------|--------------|-------------------|
| Volume 定义 | Notional = 合约数 | 需区分 Notional vs USDC |
| Double Counting | ✅ 无问题 | ⚠️ OrderFilled 需 /2 或用 OrdersMatched |
| 数据源 | 中心化 API | 链上事件 |
| 实时性 | 实时 | 区块确认延迟 |

### 4.2 HOOD 收入分析关键指标

1. **Daily Notional Volume** - API `volume_24h` 字段汇总
2. **Active Markets** - 活跃市场数量
3. **Open Interest Trend** - 市场参与度变化
4. **Category Breakdown** - 按事件类别分析（选举、经济、天气等）

---

## 5. 参考资料

- [Kalshi API Documentation](https://docs.kalshi.com/welcome)
- [Get Markets Endpoint](https://docs.kalshi.com/api-reference/market/get-markets)
- [Get Trades Endpoint](https://docs.kalshi.com/api-reference/market/get-trades)
- [Kalshi Help Center - API](https://help.kalshi.com/kalshi-api)
- [Quick Start: Market Data](https://docs.kalshi.com/getting_started/quick_start_market_data)

---

*文档生成时间: 2026-02-05*
*用途: HOOD 预测市场投资分析*
