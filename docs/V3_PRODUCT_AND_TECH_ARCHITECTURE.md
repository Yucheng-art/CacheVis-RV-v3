# V3 产品与技术架构

## 产品定位

CacheVis-RV V3 是面向计算机组成与 RISC-V Cache 教学的多实验室交互式可视化平台。它以独立 Lab 组织教学主题，使学习者能够围绕地址、缓存结构和访问过程开展分步观察与实验。

## 当前平台结构

平台外壳由以下组件组成：

- Sidebar：只展示 Home、可用学习 Lab 和 Classic Tools。
- Home：展示八个 Lab 的教学元数据、状态与入口。
- Lab Registry：集中维护 Lab 身份、分类、状态、顺序和惰性 factory。
- `QStackedWidget`：承载 Home 与 Lab 页面。

可用页面采用 lazy initialization：首次导航时通过 Registry factory 创建，此后缓存并复用，切换页面不会丢失状态。Coming Soon 页面没有 factory，不能被导航或实例化。

## Lab 状态

已实现并可用：

- Address Explorer
- Miss Type Lab
- Locality Lab
- Policy Lab
- Performance Lab
- Single Experiment
- Compare Experiment

仍为 Coming Soon：

- Write Policy Lab

Coming Soon 仅表示规划状态，不代表已有业务实现。

## 分层架构

V3 继续采用 Python、PySide6 和 `unittest`。当前代码按以下边界组织：

1. `cachevis_rv.core`：Cache 配置、行、模拟器、替换策略和统计。
2. 实验服务包：trace、runner 与 report 等可复用纯逻辑服务。
3. 独立 Lab：Address Explorer、Miss Type Lab、Locality Lab、Policy Lab、Performance Lab、Single Experiment、Compare Experiment 分别拥有自己的逻辑、controller/view model 与 widget 边界。
4. `cachevis_rv.gui`：只负责平台导航、Home、Registry、窗口协调与平台样式。

平台层不得承载 Lab 业务逻辑；不同 Lab 不得堆积在单一 Widget 中。共享能力通过明确、稳定的公共接口提供。

## M0 质量基线

- V2 稳定运行时行为保持兼容。
- 169 项 `unittest` 全部通过。
- CLI 单实验与 Compare smoke 已通过。
- GUI 入口、页面懒加载、页面缓存与 V3.0 应用身份已验证。
- Address Explorer 语义色区域具有明确的高对比度文字。

## M1 Miss Type Lab

Miss Type Lab 已通过 Registry 接入 Home 与 Sidebar，并沿用平台的 lazy initialization 和页面缓存机制。页面由以下区域组成：

- Experiment Controls
- Current Access
- Actual Cache
- Fully Associative Reference Cache
- Classification Evidence
- 3C Statistics
- Timeline

分类单位是 memory block，而不是原始 byte address，因此同一 block 内不同 offset 不会产生新的 compulsory miss。分类证据同时包含 seen-before、Actual Cache hit/miss 和 Reference Cache hit/miss。

Reference Cache 与 Actual Cache 容量相同、block size 相同，但采用 fully associative、单 set、LRU 结构。Actual Cache 在该 Lab 中也固定使用 LRU，以保持基础 3C 模型的严格定义，避免引入 policy miss。

历史 Timeline 选择只切换所查看步骤的 Evidence；Actual Cache、Reference Cache 和累计 Statistics 始终保持最新执行状态，不提供历史 Cache snapshot 回滚。

内置 preset 的稳定结果为：

- Compulsory demo：C C C C
- Conflict demo：C C F F
- Capacity demo：C C C A

## M2 Locality Lab

Locality Lab 已通过 Registry 接入 Home 与 Sidebar，并复用 Main Window 的 lazy page cache。教学模型采用 mutually exclusive primary evidence：

- exact address 已访问 → `TEMPORAL`
- address 未访问但 block 已访问 → `SPATIAL`
- block 未访问 → `FIRST_TOUCH`

现实访问可能同时具有多种局部性特征；互斥分类仅用于逐步教学解释。地址转换固定为：

- `block_address = address // block_size_bytes`
- `offset = address % block_size_bytes`

F/S/T 与 Cache 结果相互独立：HIT 不自动代表 Temporal，MISS 不代表没有 locality；Spatial hit 与 Temporal miss 都可能出现。

分析指标包括 address/block reuse gap、block reuse distance、same-block transition、address delta、unique address/block、hit/miss，以及 F/S/T counts 和 rates。Block reuse distance 使用 MRU→LRU distinct-block recency stack，取访问前目标 block 所在索引。

页面由 Experiment Controls、Current Access、Locality Evidence、Cache State、Block/Offset Access Map、Locality Statistics、Teaching Insight 和 Timeline 组成。历史 Timeline 选择只更新 Selected Evidence 与 SELECTED 标记；Current Access、Cache State、Statistics 和 Block Map 保持最新执行状态。

六个 preset 的稳定结果：

| Preset | F/S/T | Hits/Misses |
|---|---:|---:|
| Sequential Spatial | 2/6/0 | 6/2 |
| Fixed Stride | 8/0/0 | 0/8 |
| Loop Temporal Reuse | 1/3/4 | 7/1 |
| Block Locality | 1/3/4 | 7/1 |
| Matrix Row-Major | 4/12/0 | 12/4 |
| Matrix Column-Major | 4/12/0 | 0/16 |

Row-major 与 Column-major 访问相同 16 个地址，最终 Block Map cell 集合和 F/S 计数相同，但访问顺序及 Cache 结果不同。Column-major 仍具有 spatial locality 潜力，只是当前 Cache 组织没有有效利用它。

统计层持续验证 `F + S + T = Accesses`、`F + S = Unique Addresses`、`Hits + Misses = Accesses`。没有 reuse 样本时平均值显示 N/A。

## M3 Policy Lab

Policy Lab 已通过 Registry 接入 Home 与 Sidebar，并复用 Main Window 的 lazy page cache。三条 lane 对相同 Cache size、block size、ways、address width 与 address trace 同步运行，唯一变化是 core 正式字符串接口中的 replacement policy：`LRU`、`FIFO`、`Random`。项目当前没有正式 `ReplacementPolicy` enum，因此没有创建重复枚举。

每次访问只产生三种正式决策之一：

- `HIT`：目标 tag 已在映射 set 中，不 fill、不 eviction。
- `INVALID_FILL`：目标 tag 不在 set 中，但存在 invalid way；填充空 way，不驱逐有效 line，也不属于 replacement。
- `EVICTION`：目标 tag 不在 set 中且 set 已满，才按 replacement policy 选择 victim。

LRU 根据 `last_used` 选择最久未使用候选，hit 会更新 recency；FIFO 根据 `insert_time` 选择最早插入候选，hit 不刷新 insertion order；Random 将所有 valid ways 视为候选，使用可复现的 seeded replay，不代表最优、最旧或最少使用。

Random lane 由 Session 持有独立的 `random.Random(seed)` 状态。每次 Random access 临时把该私有状态交给模块级 `random`，正式调用一次 `CacheSimulator.access`，保存更新后的 Session 私有状态，并在 `finally` 中恢复进程原有的全局 random 状态。该机制不修改 core、不留下全局 `random.seed` 副作用，也不复制 Random victim 算法。

Policy Lab 分别记录 victim、state 与 outcome divergence。victim/state divergence 可以先发生，而当前三条 lane 的 HIT/MISS 仍完全相同；后续访问才可能形成 outcome divergence。页面展示完整因果链：

```text
Same address
→ Same set and tag
→ Each policy observes its own Cache state
→ HIT / INVALID FILL / EVICTION
→ Victim selection
→ Cache state divergence
→ Possible future HIT/MISS divergence
```

页面由 Experiment Controls、Preset Teaching Insight、Current Access、Divergence Summary、Selected Decision Evidence、Latest Cache State、Statistics Comparison 和 Timeline 组成。历史 Timeline 选择只更新 `selected_step`、Selected Decision Evidence 与 Timeline SELECTED；Current Access、三条 Cache state、Statistics、Divergence Summary、Random stream 和 `next_step_index` 均保持最新状态。

七个内置 preset 的稳定结果：

| Preset | LRU | FIFO | Random |
|---|---:|---:|---:|
| No Replacement Pressure | 2H / 2M | 2H / 2M | 2H / 2M |
| Victim Divergence Before Outcome | 1H / 3M | 1H / 3M | 1H / 3M |
| LRU Advantage | 2H / 3M | 1H / 4M | 1H / 4M |
| FIFO Advantage | 1H / 4M | 2H / 3M | 2H / 3M |
| Set-Local Pressure | 1H / 4M | 2H / 3M | 2H / 3M |
| Direct-Mapped Control | 0H / 4M | 0H / 4M | 0H / 4M |
| Seeded Random Replay | 0H / 8M | 0H / 8M | 0H / 8M |

每条 lane 持续验证 `Hits + Misses = Accesses` 和 `Invalid Fills + Evictions = Misses`；比较层验证 `All Agree + Outcome Divergence = Accesses`。current trace leader 只描述当前有限 trace，不代表策略普遍最优。

## M4 Performance Lab

Performance Lab 已通过 Registry 接入 Home 与 Sidebar，并复用 Main Window 的 lazy page cache。它研究显式 timing assumptions 下的教学性能模型，不测量宿主机 Python wall-clock 时间。

单级模型为：

```text
effective_miss_penalty = fixed_miss_overhead + block_size × transfer_cycles_per_byte
lookup_cycles = accesses × hit_time
miss_penalty_cycles = misses × effective_miss_penalty
total_cycles = lookup_cycles + miss_penalty_cycles
AMAT = total_cycles / accesses
     = hit_time + miss_rate × effective_miss_penalty
```

每次 access 都支付 hit time；只有 miss 支付额外 penalty，且 penalty 不重复包含 hit time。Traffic 使用 `line_fills = misses` 与 `bytes_fetched = misses × block_size`，当前不计算 write-back traffic。空 trace 的 AMAT、bytes/access、stall fraction 和 speedup 显示 N/A，不产生 NaN 或 infinity。

六个正式 sweep 为 Capacity Knee、Sequential Block Benefit、Stride Block Cost、Associativity Conflict Relief、Miss Penalty Sensitivity 和 Hit Rate Is Not AMAT。CACHE_SIZE、BLOCK_SIZE、ASSOCIATIVITY、MISS_PENALTY、HIT_TIME 分别限制只改变对应变量；CUSTOM 允许 config 与 timing 同时变化。每个 point 由 `PerformanceRunner` 从冷 Cache 独立执行，支持 LRU/FIFO，Random 属于 Policy Lab。

页面由 Sweep Controls、Point Editor、Sweep Summary、QPainter Metric Chart、Sweep Point Comparison Table、Selected Point Detail、Hit Rate vs AMAT Tradeoff 和 Analytical L1/L2 AMAT 组成。图表支持 AMAT、Hit Rate、Miss Rate、Total Cycles、Bytes Fetched、Miss Stall Fraction 和 Speedup，未增加 matplotlib、numpy、pandas 或 QtCharts 依赖。

selected point 与 chart metric 是纯展示状态：选点不重跑 sweep，也不改变 `SweepResult`、best/tie、comparison 或 hierarchy；切换 metric 只更新 chart series。Sweep 与 hierarchy 相互独立，分别运行和清理。

Analytical L1/L2 使用：

```text
AMAT = L1 hit time
     + L1 miss rate × L2 hit time
     + L1 miss rate × L2 local miss rate × memory penalty
```

L2 local miss rate 的分母是到达 L2 的访问；L2 global miss rate 的分母是全部 CPU memory accesses，`global = L1 miss rate × L2 local miss rate`。当前模型没有实际 L2 contents、inclusion/exclusion、write-back traffic 或 parallel lookup。

## 当前质量基线

- 620 项 `unittest` 全部通过，无 skip。
- M0 的 CLI、GUI、页面懒加载和 V2 兼容行为继续由回归测试覆盖。
- Miss Type Lab 的三组 preset、双 Cache、Evidence、Statistics、Timeline 和页面状态保持已完成 smoke 与人工视觉验收。
- Locality Lab 的六组 preset、Evidence、Cache、Block Map、Statistics、Timeline、平台导航与状态保持已完成 Qt smoke 和用户人工视觉验收。
- Policy Lab 的七组 preset、三策略决策证据、Cache、Divergence、Statistics、Timeline、平台导航与状态保持已完成 Qt smoke、真实 GUI 启动和用户人工视觉验收。
- Performance Lab 的六组 sweep、七指标图表、selected point、tradeoff、analytical L1/L2、平台导航与状态保持已完成 Qt smoke、真实 GUI 启动和用户人工视觉验收。

下一阶段为 M5 Write Policy Lab，仍按“纯逻辑 → `unittest` → GUI”的顺序推进。
