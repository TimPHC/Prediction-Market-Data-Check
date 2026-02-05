# Dune 验证查询结果

## 查询信息
- **Query ID**: 6657972
- **执行时间**: 2026-02-05
- **数据源**: `polymarket_polygon.ctfexchange_evt_orderfilled`

## SQL 查询
```sql
SELECT
    date_trunc('day', evt_block_time) AS day,
    COUNT(*) AS total_events,
    COUNT(DISTINCT evt_tx_hash) AS unique_txs,
    ROUND(CAST(COUNT(*) AS DOUBLE) / COUNT(DISTINCT evt_tx_hash), 2) AS events_per_tx
FROM polymarket_polygon.ctfexchange_evt_orderfilled
WHERE evt_block_time >= NOW() - INTERVAL '7' day
GROUP BY 1
ORDER BY 1 DESC
```

## 查询结果

| 日期 | 总事件数 | 唯一交易数 | 事件/交易比 |
|------|---------|-----------|------------|
| 2026-02-05 | 2,961,387 | 1,136,859 | **2.60** |
| 2026-02-04 | 5,089,299 | 1,904,711 | **2.67** |
| 2026-02-03 | 4,976,409 | 1,847,691 | **2.69** |
| 2026-02-02 | 4,730,347 | 1,778,985 | **2.66** |
| 2026-02-01 | 4,260,635 | 1,599,725 | **2.66** |
| 2026-01-31 | 4,847,590 | 1,822,935 | **2.66** |
| 2026-01-30 | 4,413,924 | 1,642,809 | **2.69** |

## 关键发现

### 1. Double Counting 问题确认
- **events_per_tx 平均值约为 2.6-2.7**
- 这意味着每笔 Polymarket 交易平均产生 2.6-2.7 个 `OrderFilled` 事件
- 简单求和所有 `OrderFilled` 事件会导致交易量被高估 **~2.6x**

### 2. 与 Paradigm 文章的一致性
- Paradigm 文章指出问题源于 maker-focused 和 taker-focused 事件的冗余
- 我们的数据验证了这一点：2.6-2.7 个事件/交易 ≈ 1 个 taker-focused + 1.6-1.7 个 maker-focused 事件

### 3. 实际影响
- 如果某 dashboard 报告日交易量为 $10B
- 实际正确的交易量应该约为 **$10B / 2.65 ≈ $3.77B**
- 差异约为 **165%**

## 结论

**Double counting 问题已通过链上数据验证确认！**

正确的统计方法应该：
1. 只计算 taker-side volume（单边）
2. 或使用 `OrdersMatched` 事件
3. 或对 `OrderFilled` 求和后除以 ~2.65

---

*查询链接: https://dune.com/queries/6657972*
