
    -- Polymarket Double Counting 验证查询
    -- 比较不同统计方法的结果差异

    WITH order_filled_events AS (
        -- 获取所有 OrderFilled 事件
        SELECT
            evt_tx_hash,
            evt_block_time,
            maker,
            taker,
            makerAssetId,
            takerAssetId,
            makerAmountFilled,
            takerAmountFilled,
            -- 判断是 maker-focused 还是 taker-focused
            CASE
                WHEN taker IN (
                    0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e,  -- CTF Exchange
                    0xc5d563a36ae78145c45a50134d48a1215220f80a   -- NegRisk CTF
                ) THEN 'taker_focused'
                ELSE 'maker_focused'
            END AS event_type
        FROM polymarket_polygon.CTFExchange_evt_OrderFilled
        WHERE evt_block_time >= NOW() - INTERVAL '7' day
    ),

    -- 方法1: 错误方法 - 求和所有 OrderFilled
    method1_wrong AS (
        SELECT
            date_trunc('day', evt_block_time) AS day,
            SUM(CAST(takerAmountFilled AS DOUBLE) / 1e6) AS volume_usd
        FROM order_filled_events
        WHERE takerAssetId = 0  -- USDC
        GROUP BY 1
    ),

    -- 方法2: 正确方法 - 只计算 taker-focused 事件
    method2_taker AS (
        SELECT
            date_trunc('day', evt_block_time) AS day,
            SUM(CAST(takerAmountFilled AS DOUBLE) / 1e6) AS volume_usd
        FROM order_filled_events
        WHERE event_type = 'taker_focused'
          AND takerAssetId = 0
        GROUP BY 1
    ),

    -- 方法3: 正确方法 - 只计算 maker-focused 事件
    method3_maker AS (
        SELECT
            date_trunc('day', evt_block_time) AS day,
            SUM(CAST(makerAmountFilled AS DOUBLE) / 1e6) AS volume_usd
        FROM order_filled_events
        WHERE event_type = 'maker_focused'
          AND makerAssetId = 0
        GROUP BY 1
    )

    -- 比较结果
    SELECT
        m1.day,
        m1.volume_usd AS wrong_method_volume,
        m2.volume_usd AS taker_side_volume,
        m3.volume_usd AS maker_side_volume,
        m1.volume_usd / NULLIF(m2.volume_usd, 0) AS double_count_ratio
    FROM method1_wrong m1
    LEFT JOIN method2_taker m2 ON m1.day = m2.day
    LEFT JOIN method3_maker m3 ON m1.day = m3.day
    ORDER BY m1.day DESC
    