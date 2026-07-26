# V3 M4 Performance Lab 总结

## 里程碑结果

M4 已完成显式 timing 与 performance core、Controller/View Models、独立 PySide6 GUI 和平台接入。Performance Lab 已从 Coming Soon 迁移为 Available，可从 Home 与 Sidebar 打开；Registry 延迟创建页面，Main Window 的通用 lazy page cache 复用页面实例并保持 sweep 与 hierarchy 状态。

M4 完成时共有 620 项 `unittest` 全部通过，无 skip。Qt offscreen smoke、真实 GUI 入口运行和用户人工视觉验收均已通过。

Performance Lab 描述显式时序假设下的教学模型，不测量宿主机 Python 程序的 wall-clock 运行时间，也不把解释器或操作系统耗时当作 Cache 性能。

## 单级 Cache 性能模型

```text
effective_miss_penalty_cycles
    = fixed_miss_overhead_cycles
    + block_size_bytes × transfer_cycles_per_byte

total_lookup_cycles
    = accesses × hit_time_cycles

total_miss_penalty_cycles
    = misses × effective_miss_penalty_cycles

total_cycles
    = total_lookup_cycles + total_miss_penalty_cycles

amat_cycles
    = total_cycles / accesses
    = hit_time_cycles + miss_rate × effective_miss_penalty_cycles
```

每次 access 都支付 hit time；只有 miss 支付额外 miss penalty。miss penalty 不包含已经支付的 hit time。

Traffic 模型：

- `line_fills = misses`
- `bytes_fetched = misses × block_size_bytes`
- 当前不计算 write-back traffic

空 trace 的 accesses、hits、misses 和 cycles 为 0；AMAT、bytes/access、miss stall fraction 和 speedup 为 N/A，不产生 NaN 或 infinity。

## Sweep、Speedup 与执行边界

六个教学 sweep：

1. Capacity Knee
2. Sequential Block Benefit
3. Stride Block Cost
4. Associativity Conflict Relief
5. Miss Penalty Sensitivity
6. Hit Rate Is Not AMAT

单变量约束：

- `CACHE_SIZE`：只允许 Cache size 变化。
- `BLOCK_SIZE`：只允许 block size 变化；effective miss penalty 可随 block size 改变。
- `ASSOCIATIVITY`：只允许 ways 变化。
- `MISS_PENALTY`：只允许 fixed miss overhead 变化。
- `HIT_TIME`：只允许 hit time 变化。
- `CUSTOM`：允许 config 与 timing 同时变化。

```text
speedup_vs_baseline = baseline_total_cycles / current_total_cycles
```

speedup 大于 1 表示快于 baseline，小于 1 表示慢于 baseline，baseline 自身为 1；零周期时为 N/A。

`PerformanceRunner` 对每个 point 从空 Cache 冷启动，不复用前一 point 的 Cache 状态。正式支持 LRU、FIFO；Random 明确拒绝，Random 性能排名属于 Policy Lab。

## 六个 Preset 的稳定结果

### Capacity Knee

Trace 为 `0, 4, 8, 12` 重复四轮。

| Cache | Hits/Misses | AMAT |
|---|---:|---:|
| 8B | 0H / 16M | 23 |
| 16B | 12H / 4M | 6.5 |
| 32B | 12H / 4M | 6.5 |

16B 与 32B 为 best AMAT tie。工作集装入后继续增加容量没有改善当前 trace；这不表示 Cache 越大永远越好。

### Sequential Block Benefit

| Block | Hits/Misses | AMAT |
|---|---:|---:|
| 4B | 0H / 8M | 23 |
| 8B | 4H / 4M | 13 |
| 16B | 6H / 2M | 8 |

大 block 利用顺序访问的空间局部性并减少 miss，同时增加单次 fill penalty。

### Stride Block Cost

| Block | Hits/Misses | AMAT |
|---|---:|---:|
| 4B | 0H / 4M | 23 |
| 8B | 0H / 4M | 25 |
| 16B | 0H / 4M | 29 |

miss 数完全相同；大 block 没有带来命中收益，penalty、traffic 和 AMAT 反而增加。

### Associativity Conflict Relief

| Ways | Hits/Misses | AMAT |
|---|---:|---:|
| 1-way | 0H / 6M | 23 |
| 2-way | 4H / 2M | 约 8.3333 |
| 4-way | 4H / 2M | 约 8.3333 |

2-way 与 4-way tie，相联度缓解当前 trace 的 conflict。hit time 在实验中是明确固定输入，因此不能据此宣称真实硬件的高相联度没有时序成本。

### Miss Penalty Sensitivity

三个 point 的 Cache 行为均为 2H / 2M、miss rate 0.5。

| Fixed overhead | AMAT |
|---|---:|
| 10 | 6 |
| 50 | 26 |
| 100 | 51 |

相同 miss rate 在不同 miss penalty 下可以产生完全不同的性能损失。

### Hit Rate Is Not AMAT

| Point | Hits/Misses | Hit Rate | AMAT |
|---|---:|---:|---:|
| Fast Small | 0H / 4M | 0 | 11 |
| Slow Large | 2H / 2M | 0.5 | 13 |

Slow Large 命中率更高，但较高 hit time 使其 AMAT 更差。不能只按 hit rate 排名，也不宣称 Fast Small 对所有 workload 都更好。

best AMAT、best hit rate、lowest traffic、fastest 和 slowest 均支持 tie，不随意只取第一个 point。current trace leader 只代表当前 trace，不代表配置普遍最优。

## 页面与选择语义

页面组成：

- Sweep Controls
- Point Editor
- Sweep Summary
- Metric Chart
- Sweep Point Comparison Table
- Selected Point Detail
- Hit Rate vs AMAT Tradeoff
- Analytical L1/L2 AMAT

Metric Chart 支持 AMAT、Hit Rate、Miss Rate、Total Cycles、Bytes Fetched、Miss Stall Fraction 和 Speedup。图表使用 PySide6 自定义 `QWidget`/`QPainter`，没有新增 matplotlib、numpy、pandas 或 QtCharts 依赖。

选择 point 只更新 selected point ID/detail、table selected 和 chart selected 标记；不重新运行 sweep，也不改变 `SweepResult`、best/tie、comparison 或 hierarchy。切换 chart metric 只更新 chart 数据，同样不重跑 sweep。

Sweep 与 Hierarchy 完全独立：Run Sweep 不清除 Hierarchy，Analyze Hierarchy 不清除 Sweep，Clear Sweep 不清除 Hierarchy，Clear Hierarchy 不清除 Sweep。

## Analytical L1/L2

```text
amat_cycles
    = l1_hit_time_cycles
    + l1_miss_rate × l2_hit_time_cycles
    + l1_miss_rate × l2_local_miss_rate × memory_penalty_cycles

l1_hit_probability = 1 - l1_miss_rate
l2_global_hit_probability = l1_miss_rate × (1 - l2_local_miss_rate)
memory_access_probability = l1_miss_rate × l2_local_miss_rate
l2_global_miss_rate = memory_access_probability
```

L2 local miss rate 的分母是到达 L2 的访问；L2 global miss rate 的分母是所有 CPU memory accesses。`global = L1 miss rate × L2 local miss rate`。

Analytical L1/L2 Example：

- 输入：L1 hit time 1、L1 miss rate 0.10、L2 hit time 8、L2 local miss rate 0.25、memory penalty 80。
- 概率：L1 hit 0.90、L2 global hit 0.075、main memory 0.025。
- contributions：L1 1.0、L2 0.8、memory 2.0。
- AMAT：3.8 cycles。

限制：Analytical model only；No actual L2 contents；No inclusion/exclusion behavior；No write-back traffic；No parallel lookup model。当前没有实际第二级 CacheSimulator。

## 持续验证的不变量

- Hits + Misses = Accesses
- Line Fills = Misses
- Bytes Fetched = Misses × Block Size
- Total Cycles = Lookup Cycles + Miss Penalty Cycles
- AMAT × Accesses = Total Cycles
- Probability outcomes sum to 1
- L1 + L2 + Memory contributions = AMAT

## 尚未实现与下一阶段

当前仍未实现：

- Write Policy Lab
- 实际 L2 Cache hierarchy simulator
- inclusion / exclusion
- write-back traffic
- parallel lookup
- pipeline CPI
- energy model
- hardware-derived hit-time model
- animation
- performance report export

下一阶段为 M5 Write Policy Lab。
