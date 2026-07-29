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
- Write Policy Lab
- Single Experiment
- Compare Experiment

当前 8 个 Lab 全部 Available，Coming Soon 为 0。

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

- 720 项 `unittest` 全部通过，无 skip。
- M0 的 CLI、GUI、页面懒加载和 V2 兼容行为继续由回归测试覆盖。
- Miss Type Lab 的三组 preset、双 Cache、Evidence、Statistics、Timeline 和页面状态保持已完成 smoke 与人工视觉验收。
- Locality Lab 的六组 preset、Evidence、Cache、Block Map、Statistics、Timeline、平台导航与状态保持已完成 Qt smoke 和用户人工视觉验收。
- Policy Lab 的七组 preset、三策略决策证据、Cache、Divergence、Statistics、Timeline、平台导航与状态保持已完成 Qt smoke、真实 GUI 启动和用户人工视觉验收。
- Performance Lab 的六组 sweep、七指标图表、selected point、tradeoff、analytical L1/L2、平台导航与状态保持已完成 Qt smoke、真实 GUI 启动和用户人工视觉验收。
- Write Policy Lab 的七组 preset、四 lane decision/cache/traffic/statistics、historical evidence、timeline、平台导航与状态保持已完成 Qt smoke、真实 GUI 启动和用户人工视觉验收。

M0–M5 功能里程碑已完成；下一阶段为 V3 Final Release Hardening，本次不包含该阶段工作。

## M5 Write Policy Lab

### 分层与调用边界

M5 延续纯逻辑、应用状态与 GUI 分离的结构：

- 正式 Core：`CacheConfig`、`CacheSimulator.access(address, operation)`、dirty line 和正式 `AccessResult` 证据。
- M5.1 Domain：parser、explainer、traffic model、four-lane session 与 presets。
- M5.2 Application：`WritePolicyController`、`WritePolicyPageState`、immutable View Models 与 historical selection。
- M5.3 Presentation：`WritePolicyLabWidget`、controls、decision cards、cache panels、traffic comparison、statistics、timeline、divergence 与 comparison summary。

```text
WritePolicyLabWidget
        ↓
WritePolicyController
        ↓
WritePolicyComparisonSession
        ├── WT + WA CacheSimulator
        ├── WT + NWA CacheSimulator
        ├── WB + WA CacheSimulator
        └── WB + NWA CacheSimulator
```

四条 lane 使用独立 simulator，不从任一 lane 复制结果。正式 `CacheSimulator` 决定 Cache 行为，Explainer 只解释正式结果，Traffic model 根据正式事件计算教学流量；GUI 只消费 View Model，不直接访问 `CacheSimulator`，也不重新实现策略语义。

### Core 写策略契约

`CacheConfig` 默认 `write_policy="write-through"`、`write_allocate=True`，正式支持 WT+WA、WT+NWA、WB+WA、WB+NWA。Write-Through write hit 保持 line clean 并立即向 lower memory 写 store；Write-Back write hit 将 line 标记为 dirty，不立即写 lower memory。

Write miss + Write-Allocate 会分配 line 并产生 block fill：WT 新 line clean 且立即写 store，WB 新 line dirty 且不立即写 store。Write miss + No-Write-Allocate 是 MISS：不分配、不选择 victim、不改变 Cache state 或 replacement metadata，store 直接 bypass。Read miss 无论 `write_allocate` 为何都分配 clean line，并可驱逐 dirty victim。替换 dirty valid line 会产生整个 block 的 write-back。

正式 `AccessResult` 提供 `allocated`、`bypassed`、`hit_way`、`fill_way`、`evicted_way`、`victim_tag`、`victim_dirty`、`line_dirty_before` 和 `line_dirty_after`。实际 eviction 以 `evicted_way` 为准；`victim_way` 仅为旧兼容字段。victim tag/dirty 在覆盖前取得，invalid fill 不报告真实 victim，bypass 不含 hit/fill/eviction way，结果也不暴露 `CacheLine`。

### 四 lane、decision 与 trace

固定 lane 顺序为 `wt_wa`、`wt_nwa`、`wb_wa`、`wb_nwa`。正式 decision kind 只有：`READ_HIT`、`READ_MISS_FILL`、`WRITE_HIT_THROUGH`、`WRITE_HIT_BACK`、`WRITE_MISS_ALLOCATE_THROUGH`、`WRITE_MISS_ALLOCATE_BACK`、`WRITE_MISS_BYPASS`；不存在 UNKNOWN/OTHER，dirty eviction 是附带事件，不替代主 decision。

Trace parser 接受逐行或逗号分隔的 `R 0`、`W 4`、`R 0x10`、`W 0x20`，操作符大小写均可，也接受 `R:0` / `W:0x10`；空文本是正式空 trace。裸地址、未知操作、缺地址、非法或负地址、额外字段及连续逗号形成的空项均拒绝。

### Traffic 与 final drain

`WriteTrafficAssumptions.store_size_bytes` 必须为正整数且不大于 block size；store 不得跨 block。模型不支持 partial dirty-byte mask，也不自动拆分跨 block write。

```text
block_fill_bytes = block_fills × block_size_bytes
immediate_store_bytes = immediate_store_writes × store_size_bytes
bypass_write_bytes = bypass_writes × store_size_bytes
dirty_writeback_bytes = dirty_writebacks × block_size_bytes

memory_read_transactions = block_fills
memory_read_bytes = block_fill_bytes
memory_write_transactions = immediate_store_writes + bypass_writes + dirty_writebacks
memory_write_bytes = immediate_store_bytes + bypass_write_bytes + dirty_writeback_bytes
total_lower_memory_transactions = memory_read_transactions + memory_write_transactions
total_lower_memory_bytes = memory_read_bytes + memory_write_bytes
```

这些 lower-memory traffic 均为教学分析值，不是宿主机真实 I/O。运行结束时，`final_dirty_lines` 是仍 valid 且 dirty 的 resident line 数，`final_dirty_bytes = final_dirty_lines × block_size_bytes`。`memory_write_bytes_with_final_drain = memory_write_bytes + final_dirty_bytes`，`total_lower_memory_bytes_with_final_drain = total_lower_memory_bytes + final_dirty_bytes`。Final drain 只是非变异分析值，不是 trace step、不调用 flush、不修改 Cache，也不会重复计算已被 eviction 写回的 line；runtime 与 including-final-drain 必须分开。

### 不变量与 divergence

每条 lane 持续满足：

```text
accesses = reads + writes
hits + misses = accesses
read_hits + read_misses = reads
write_hits + write_misses = writes
write_miss_allocations + write_miss_bypasses = write_misses
block_fills = read_misses + write_miss_allocations
dirty_writebacks = dirty_evictions
memory_read_bytes = block_fills × block_size_bytes
memory_write_bytes = immediate_store_writes × store_size_bytes
                   + bypass_writes × store_size_bytes
                   + dirty_writebacks × block_size_bytes
total_lower_memory_bytes = memory_read_bytes + memory_write_bytes
final_dirty_bytes = final_dirty_lines × block_size_bytes
total_lower_memory_bytes_with_final_drain = total_lower_memory_bytes + final_dirty_bytes
```

比较层满足 `all_outcomes_agree_steps + outcome_divergence_steps = accesses`。七类 divergence 分别比较：四 lane HIT/MISS outcome、allocation、bypass、当前步骤 dirty writeback、当前步骤 lower-memory total bytes、每个位置的 `valid and dirty`，以及包括 valid/tag/dirty/last_used/insert_time 的完整 snapshot。Dirty-state divergence 不等于 full cache-state divergence，后者也不只是比较 tag 集合。

### 历史选择与当前状态

Selected Historical Evidence 展示 selected step 的 access、四 lane decisions、traffic delta 与 divergence flags。Current Run State 始终展示最新 Session Cache、累计 statistics、final dirty state、`next_step_index` 与完整 timeline。

选择历史 step 只改变 `selected_step_index`、`selected_step`、selected decisions 和 timeline selected 标记；不会改变 `latest_step_index`、`next_step_index`、completion、current Cache、current statistics、final dirty state、divergence counts 或 comparison summary。页面明确提示：`Viewing historical evidence; cache and statistics remain at the latest run state.`

### Presentation 与平台

页面由 Experiment Controls、Teaching Summary、Current Access and Run Position、Divergence Summary、Selected Historical Decision Cards、Current Four-Lane Cache State、Runtime / Final Drain Traffic Comparison、Current Cumulative Statistics、Timeline 和 Policy Comparison Summary 组成。整体采用纵向 `QScrollArea`，四 lane Cache 为 2×2；宽表格与 timeline 支持横向滚动。Traffic Canvas 使用 QWidget + QPainter，不引入 matplotlib、numpy、pandas 或 QtCharts；精确数字表与图形并存，状态不只依赖颜色表达。

Comparison Summary 支持 runtime / with-drain 最低流量 lane、最高 hit-rate lane、tie、两种 leader 是否一致，以及 allocation 对 future outcome、propagation 对 dirty state/runtime traffic、dirty eviction、bypass、actual observations 和 caution note。固定提示为：`Results apply only to the current trace, cache configuration, and traffic assumptions.`

平台当前为 Learn 6 个（Address Explorer、Miss Type、Locality、Policy、Performance、Write Policy）加 Classic Tools 2 个（Single Experiment、Compare Experiment），共 8 Available、0 Coming Soon。Home、Sidebar、Registry 与 Main Window 通用 lazy page cache 正常；Write Policy 首次导航延迟创建，再次导航复用实例并保持 experiment、timeline、selection、Cache 与 statistics，Main Window 没有 Write Policy 专用 if/elif。

### 明确未实现

当前未实现 store buffer、write combining、partial dirty-byte mask、跨 block store 拆分、atomic operations、cache coherence、memory consistency、non-temporal stores、实际 lower-memory latency、pipeline CPI、L2 Cache hierarchy、prefetch、energy model、animation、Write Policy 专用报告导出或实际硬件实现。
