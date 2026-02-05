# 预测市场平台数据统计口径对比

## 1. 平台概览

| 平台 | 类型 | 区块链 | 数据来源 | Double Counting 风险 |
|------|------|--------|----------|---------------------|
| **Polymarket** | 去中心化 CLOB | Polygon | 链上事件 | ⚠️ 高 (OrderFilled 事件冗余) |
| **Kalshi** | 中心化 | N/A | API | ✅ 无 (中心化数据库) |
| **Opinion** | 去中心化 | 多链 | 链上事件 | ⚠️ 需验证 |
| **Limitless** | 去中心化 AMM | Base | 链上事件 | ⚠️ 需验证 (AMM 结构) |
| **Myriad** | 去中心化 | Abstract/多链 | 链上事件 | ⚠️ 需验证 |
| **ForecastEx** | 待确认 | 待确认 | 待确认 | 待确认 |
| **Predict.fun** | 去中心化 | 待确认 | 链上事件 | ⚠️ 需验证 |
| **Overtime** | 去中心化 | 多链 | 链上事件 | ⚠️ 需验证 |

## 2. Polymarket 详细分析

### 2.1 数据源
- **合约地址**:
  - CTF Exchange: `0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e`
  - NegRisk CTF Exchange: `0xc5d563a36ae78145c45a50134d48a1215220f80a`
  - Conditional Tokens: `0x4d97dcd97ec945f40cf65f87097ace5ea0476045`

### 2.2 事件结构
| 事件类型 | 数量/交易 | 是否冗余 |
|----------|-----------|----------|
| `OrderFilled` (maker-focused) | ≥1 | 否 |
| `OrderFilled` (taker-focused) | =1 | **是** (与 maker-focused 冗余) |
| `OrdersMatched` | =1 | 否 |

### 2.3 统计方法对比
| 方法 | 描述 | 正确性 | 结果比例 |
|------|------|--------|----------|
| Sum all `OrderFilled` | 求和所有事件 | ❌ 错误 | 2x |
| Taker-side only | 只计算 taker 侧 | ✅ 正确 | 1x |
| Maker-side only | 只计算 maker 侧 | ✅ 正确 | 1x |
| `OrdersMatched` | 使用汇总事件 | ✅ 正确 | 1x |

### 2.4 复杂交易影响
对于包含 Split/Merge 的交易，double counting 的影响可能更大：
- **Swap 交易**: 2x 错误
- **Split/Merge 交易**: 可能 >10x 错误 (取决于交易结构)

## 3. Kalshi 详细分析

### 3.1 数据源
- **类型**: 中心化 API
- **监管**: CFTC 监管
- **数据特点**: 直接记录 Maker/Taker 侧

### 3.2 统计方法
| 指标 | Kalshi 定义 |
|------|-------------|
| Notional Volume | 合约数量 × 结算价值 ($1) |
| Taker Volume | Taker 侧的 USD 流量 |
| 费用结构 | 2025年前仅 Taker 付费 |

### 3.3 Double Counting 风险
- ✅ **无风险** - 中心化数据库直接记录交易
- 数据准确性取决于 Kalshi API 的可信度

## 4. 其他平台分析

### 4.1 Opinion
- **区块链**: 多链支持
- **数据源**: 链上事件
- **费用贡献**: 2025年1月 $6.14M (市场份额 56%)
- **风险评估**: 需要分析其智能合约事件结构

### 4.2 Limitless
- **区块链**: Base
- **模式**: AMM (Automated Market Maker)
- **交易量**: 累计 >$500M
- **风险评估**: AMM 模式可能有不同的统计问题

### 4.3 Myriad
- **区块链**: Abstract, Linea, BNB
- **Dune 数据源**:
  - `myriad_abstract.predictionmarketv3_evt_marketactiontx`
  - `myriad_multichain.predictionmarketv3_4_evt_marketactiontx`
- **风险评估**: 需要分析 MarketActionTx 事件结构

## 5. Dune Dashboard 统计口径

### 5.1 datadashboards/prediction-markets
**查询 ID**: 5753743

**数据源 (27个表)**:
- Myriad 相关表 (多个版本)
- Limitless 相关表
- Polymarket 相关表
- prices.usd

**关键代码发现**:
```sql
SUM(...)/2 as Volume  -- 已经在修正 double counting
```

**当前状态**: 部分查询已修正 `/2`

### 5.2 其他 Dune Dashboards
| Dashboard | 作者 | 修复状态 |
|-----------|------|----------|
| datadashboards/prediction-markets | datadashboards | 已修复 |
| filarm/polymarket-activity | filarm | 需验证 |
| rchen8/polymarket | rchen8 | 需验证 |
| fergmolina/polymarket-markets-data | fergmolina | 需验证 |

## 6. 验证建议

### 6.1 独立验证步骤
1. **选取样本交易**: 从各平台选取代表性交易
2. **解析事件日志**: 获取完整的事件序列
3. **计算对比**: 使用不同方法计算 volume
4. **交叉验证**: 与官方数据对比

### 6.2 关键验证点
- [ ] Polymarket: 验证 taker-focused vs maker-focused 事件
- [ ] Opinion: 分析智能合约事件结构
- [ ] Limitless: 分析 AMM 交易事件
- [ ] Myriad: 分析 MarketActionTx 事件字段

### 6.3 验证工具
- Dune Analytics SQL 查询
- Polygonscan 交易解析
- Web3.py 链上数据查询
- 平台官方 API 对比

## 7. 结论

### 7.1 确认的问题
1. ✅ Polymarket 存在 double counting 问题 (如果简单求和 OrderFilled)
2. ✅ 主要数据提供商已确认并修复
3. ✅ 正确方法是使用单边 volume 或 OrdersMatched

### 7.2 待验证
1. ⏳ Opinion 智能合约是否有类似问题
2. ⏳ Limitless AMM 模式的统计口径
3. ⏳ Myriad 的事件结构

### 7.3 建议
- 使用 **taker-side volume** 作为标准统计口径
- 与 Kalshi 的 "notional taker volume" 保持一致
- 定期验证 Dune 查询的统计方法

---

## 参考资料
- [Paradigm: Polymarket Volume Is Being Double-Counted](https://www.paradigm.xyz/2025/12/polymarket-volume-is-being-double-counted)
- [Kalshi API Documentation](https://docs.kalshi.com/getting_started/quick_start_market_data)
- [Dune Prediction Markets Dashboard](https://dune.com/datadashboards/prediction-markets)
- [Kalshi Data Dashboard](https://www.kalshidata.com/)
