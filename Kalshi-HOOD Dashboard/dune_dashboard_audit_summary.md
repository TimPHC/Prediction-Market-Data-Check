# Dune Dashboard Double Counting 审计汇总

## 执行日期: 2026-02-05

## 1. 验证结论

### 1.1 Double Counting 问题已确认
通过链上数据验证，Polymarket 的 `OrderFilled` 事件确实存在 double counting 问题：

| 指标 | 数值 | 含义 |
|------|------|------|
| events_per_tx | **2.60 - 2.69** | 每笔交易平均产生 2.6-2.7 个 OrderFilled 事件 |
| 错误倍数 | **~2.6x** | 简单求和导致 volume 被高估约 160% |

### 1.2 验证方法
- **Query ID**: 6657972
- **数据源**: `polymarket_polygon.ctfexchange_evt_orderfilled`
- **时间范围**: 最近 7 天
- **样本量**: 每日 400-500 万个事件

---

## 2. Dune Dashboard 审计结果

### 2.1 汇总表

| Dashboard | 作者 | 修复状态 | 修复方法 | 备注 |
|-----------|------|----------|----------|------|
| **datadashboards/prediction-markets** | datadashboards | ✅ 已修复 | `/2` 除法修正 | 主要聚合 dashboard |
| **filarm/polymarket-activity** | filarm | ✅ 已修复 | 使用 `OrdersMatched` | 正确使用汇总事件 |
| **rchen8/polymarket** | rchen8 | ⚠️ 不适用 | 使用 AMM 数据源 | 旧架构，非 CLOB |
| **fergmolina/polymarket-markets-data** | fergmolina | ⚠️ 混合 | 混合数据源 | AMM + CLOB + Gamma API |

### 2.2 详细分析

#### A. datadashboards/prediction-markets
- **Query ID**: 5753743
- **数据源数量**: 27 个表
- **修复方式**:
  ```sql
  SUM(...)/2 as Volume
  ```
- **评估**: ✅ 正确处理了 double counting
- **覆盖平台**: Polymarket, Myriad, Limitless 等

#### B. filarm/polymarket-activity
- **数据源**: `polymarket_polygon.CTFExchange_evt_OrdersMatched`
- **修复方式**: 直接使用 `OrdersMatched` 事件
- **评估**: ✅ 最佳实践 - 每笔交易只有一个 OrdersMatched 事件
- **优点**: 无需额外修正，数据天然准确

#### C. rchen8/polymarket
- **数据源**: `polymarket_polygon.FixedProductMarketMaker_evt_*`
- **评估**: ⚠️ 使用旧版 AMM (Automated Market Maker) 架构
- **说明**:
  - Polymarket 2021-2022 年使用 AMM
  - 2023+ 迁移到 CLOB (Central Limit Order Book)
  - AMM 事件结构不同，不存在同类 double counting
  - 但数据可能不完整（不包含新 CLOB 交易）

#### D. fergmolina/polymarket-markets-data
- **数据源**:
  - `polymarketfactory_polygon.FixedProductMarketMakerFactory_evt_*` (AMM)
  - `polymarket_polygon.negriskctfexchange_*` (CLOB)
  - `dune.fergmolina.result_polymarket_gamma_*` (Gamma API)
  - `polygon.logs` (原始日志)
- **评估**: ⚠️ 混合架构
- **风险**:
  - AMM 部分无 double counting 问题
  - CLOB 部分需确认是否使用了正确方法
  - Gamma API 数据已由第三方处理

---

## 3. 正确的统计方法

### 3.1 推荐方法 (优先级排序)

1. **使用 `OrdersMatched` 事件** ⭐ 最佳
   - 每笔交易只有一个事件
   - 无需额外修正
   ```sql
   SELECT SUM(takerAmountFilled) FROM polymarket_polygon.CTFExchange_evt_OrdersMatched
   ```

2. **使用 Taker-side Volume**
   - 只计算 taker-focused 事件
   - 需要判断事件类型
   ```sql
   WHERE taker IN (0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e, 0xc5d563a36ae78145c45a50134d48a1215220f80a)
   ```

3. **除以修正系数** (简易方法)
   - 对所有 OrderFilled 求和后除以 2
   - 简单但不够精确（实际比例约 2.6-2.7）

### 3.2 错误方法 ❌

```sql
-- 错误：会导致 ~2.6x 的 volume
SELECT SUM(takerAmountFilled)
FROM polymarket_polygon.CTFExchange_evt_OrderFilled
```

---

## 4. 各平台数据口径对比

| 平台 | 类型 | Double Counting 风险 | 推荐数据源 |
|------|------|---------------------|-----------|
| **Polymarket** | 链上 CLOB | ⚠️ 高 | `OrdersMatched` 或 taker-side |
| **Kalshi** | 中心化 API | ✅ 无 | 官方 API |
| **Opinion** | 链上 | ⚠️ 待验证 | 需分析合约 |
| **Limitless** | 链上 AMM | ⚠️ 待验证 | 需分析事件结构 |
| **Myriad** | 链上 | ⚠️ 待验证 | `MarketActionTx` 事件 |

---

## 5. 关键发现

### 5.1 已确认
1. ✅ Polymarket `OrderFilled` 事件存在 double counting (2.6-2.7x)
2. ✅ 主要 Dune dashboard (datadashboards) 已修复
3. ✅ `OrdersMatched` 是最可靠的数据源
4. ✅ Kalshi 作为中心化平台，数据可信

### 5.2 待进一步验证
1. ⏳ Opinion 合约的事件结构
2. ⏳ Limitless AMM 的统计口径
3. ⏳ Myriad 的 `MarketActionTx` 事件字段
4. ⏳ fergmolina dashboard 的 CLOB 部分是否正确处理

---

## 6. 建议

### 对于数据分析
1. **首选 `OrdersMatched`** 作为 Polymarket volume 数据源
2. 使用 datadashboards/prediction-markets 作为聚合参考
3. 交叉验证时注意 AMM vs CLOB 的架构差异

### 对于投资决策
1. 历史数据（修复前）可能被高估 ~2x
2. 比较不同平台时确保口径一致
3. Kalshi 的 "notional taker volume" 与 Polymarket 修正后数据可比

---

## 参考资料

- [Paradigm: Polymarket Volume Is Being Double-Counted](https://www.paradigm.xyz/2025/12/polymarket-volume-is-being-double-counted)
- [Dune Query 6657972 - 验证查询](https://dune.com/queries/6657972)
- [datadashboards/prediction-markets](https://dune.com/datadashboards/prediction-markets)
- [Kalshi API Documentation](https://docs.kalshi.com/)

---

*报告生成时间: 2026-02-05*
*验证方法: 链上数据分析 + Dune SQL 查询*
