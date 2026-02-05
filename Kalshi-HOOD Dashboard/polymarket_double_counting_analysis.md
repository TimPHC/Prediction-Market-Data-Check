# Polymarket Double Counting 问题分析

## 1. 问题背景

根据 Paradigm 研究报告 (2025年12月), 大多数追踪 Polymarket 交易量的 dashboard 存在 **double counting（双重计算）** 问题。

### 核心问题
- 简单求和所有 `OrderFilled` 事件会导致交易量被重复计算
- 例如：一笔 $4.13 的 YES 代币卖出实际被记录为 $8.26

## 2. Polymarket 智能合约事件结构

### 2.1 两个关键事件
Polymarket 使用 2 个 EVM 事件来跟踪交易：
1. **`OrderFilled`** - 每个 maker 和 taker 各产生一个
2. **`OrdersMatched`** - 每笔交易只有一个

### 2.2 事件字段
两个事件都包含以下字段：
- `makerAssetID`: 0 (USDC) 或 YES/NO token ID
- `takerAssetID`: 0 (USDC) 或 YES/NO token ID
- `makerAmountFilled`: maker 的代币数量
- `takerAmountFilled`: taker 的代币数量

`OrderFilled` 事件额外包含：
- `maker`: maker 地址
- `taker`: taker 地址

### 2.3 每笔交易的事件序列
```
1. 至少一个 "maker-focused" OrderFilled 事件
   - 每个参与的 maker 产生一个
   - maker 字段各不相同
   - taker 字段都是同一个（整笔交易的 taker）

2. 恰好一个 "taker-focused" OrderFilled 事件
   - maker 字段是整笔交易的 taker
   - taker 字段是 Polymarket 交易所合约

3. 恰好一个 OrdersMatched 事件
   - 与 taker-focused OrderFilled 的数量相同
```

**关键点：item (2) 与 item (1) 是冗余的！taker-focused 事件不代表额外的经济活动。**

## 3. 8种交易类型

### Swap 交易 (4种)
| 类型 | Taker | Maker |
|------|-------|-------|
| 1 | 买入 YES | 卖出 YES |
| 2 | 买入 NO | 卖出 NO |
| 3 | 卖出 YES | 买入 YES |
| 4 | 卖出 NO | 买入 NO |

### Split 交易 (2种) - 增加 Open Interest
| 类型 | Taker | Maker |
|------|-------|-------|
| 5 | 买入 YES | 买入 NO |
| 6 | 买入 NO | 买入 YES |

### Merge 交易 (2种) - 减少 Open Interest
| 类型 | Taker | Maker |
|------|-------|-------|
| 7 | 卖出 YES | 卖出 NO |
| 8 | 卖出 NO | 卖出 YES |

## 4. 正确的 Volume 统计方法

### 4.1 Notional Volume (合约数量)
- 直接计算交易的合约数量
- 不受 double counting 影响（如果正确过滤）

### 4.2 Cash Flow Volume (USD 流量)
**错误方法：** 简单求和所有 `OrderFilled` 事件
- 会导致 2x 的 volume

**正确方法（任选其一）：**
1. **Taker-side volume**: 只计算 taker 方的 USD 流量
2. **Maker-side volume**: 只计算 maker 方的 USD 流量
3. **OrdersMatched**: 使用 `OrdersMatched` 事件

## 5. Dune Dashboard 统计口径分析

### 5.1 datadashboards/prediction-markets
- **数据源**: 27个表，包括多个平台
- **发现**: 部分代码使用 `/2` 修正 double counting
- **代码示例**:
  ```sql
  SUM(...)/2 as Volume
  ```

### 5.2 受影响的 Dashboard（修复前）
根据 Paradigm 文章，以下 dashboard 曾经 double counting：
- DefiLlama
- Allium Labs
- Blockworks
- 多个 Dune dashboards

### 5.3 Kalshi 数据源
- Kalshi 是中心化平台，数据来自 API
- 不存在链上 double counting 问题
- 统计口径：notional taker volume

## 6. 影响评估

### 修复前后对比（2024年10-11月）
| 月份 | 修复前报告 | 修复后实际 |
|------|-----------|-----------|
| 2024-10 | ~$2.5B | ~$1.25B |
| 2024-11 | ~$2.5B | ~$1.25B |

**影响：实际交易量约为报告值的 50%**

## 7. 验证方法

### 7.1 链上数据验证
1. 选取特定交易 tx hash
2. 解析所有 `OrderFilled` 事件
3. 分析 maker-focused vs taker-focused 事件
4. 计算不同统计方法的结果差异

### 7.2 关键合约地址
- CTF Exchange: `0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e`
- NegRisk CTF Exchange: `0xc5d563a36ae78145c45a50134d48a1215220f80a`

## 8. 结论

1. **Double counting 问题确实存在** - 由于 Polymarket 合约的事件设计
2. **不是 Polymarket 的错误** - 而是数据分析师对合约结构理解不足
3. **正确统计方法** - 使用单边 volume (taker 或 maker) 或 OrdersMatched
4. **行业影响** - 主要数据提供商已确认并修复

## 参考资料
- [Paradigm: Polymarket Volume Is Being Double-Counted](https://www.paradigm.xyz/2025/12/polymarket-volume-is-being-double-counted)
- [Polymarket CLOB Documentation](https://docs.polymarket.com/developers/CLOB/introduction)
- [Volume Simulator Spreadsheet](https://docs.google.com/spreadsheets/d/1oqqb7J-rb6-kw4rKBK-H-SWtJfOLV7PuYcCPZpgkPv8)
