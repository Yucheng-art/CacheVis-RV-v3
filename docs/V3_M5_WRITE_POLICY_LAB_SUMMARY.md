# V3 M5 Write Policy Lab 总结

## 里程碑范围

M5 完成了正式 Core 写策略扩展、纯逻辑语义与流量比较、Controller/View Models、独立 GUI 和平台接入。平台现有 8 个 Available Lab、0 个 Coming Soon。M5 不实现 store buffer、write combining、partial dirty-byte mask、跨 block store 拆分、atomic operations、cache coherence、memory consistency、non-temporal stores、实际 lower-memory latency、pipeline CPI、L2 hierarchy、prefetch、energy model、animation、Write Policy 专用报告导出或实际硬件实现。

## 正式 Core 契约

`CacheConfig` 默认 `write_policy="write-through"`、`write_allocate=True`，所以未显式指定新字段的旧调用保持既有行为。正式支持 WT+WA、WT+NWA、WB+WA、WB+NWA。

- Write-Through hit：HIT，line 保持 clean，产生 immediate lower-memory store。
- Write-Back hit：HIT，line 标记 dirty，不立即写 lower memory。
- Write miss + WA：MISS，分配 line 并 block fill；WT line clean 且立即 store，WB line dirty 且不立即 store。
- Write miss + NWA：MISS，不分配、不选择 victim、不改变 Cache 或 replacement metadata，store bypass。
- Read miss：无论 `write_allocate` 为何都分配 clean line，并可能驱逐 dirty victim。
- Dirty eviction：覆盖 dirty valid line 时写回整个 block。

正式 `AccessResult` 暴露：`allocated`、`bypassed`、`hit_way`、`fill_way`、`evicted_way`、`victim_tag`、`victim_dirty`、`line_dirty_before`、`line_dirty_after`。实际 eviction 只以 `evicted_way` 为准；`victim_way` 仅保留兼容用途。victim tag/dirty 在覆盖前记录，invalid fill 不报告真实 victim，bypass 不含 hit/fill/eviction way，也不向调用方暴露 `CacheLine`。

## Domain 与 Application

四条独立 lane 固定为：

1. `wt_wa` — WT + WA
2. `wt_nwa` — WT + NWA
3. `wb_wa` — WB + WA
4. `wb_nwa` — WB + NWA

每条 lane 拥有独立 `CacheSimulator`。七个且仅七个 decision kind 为：`READ_HIT`、`READ_MISS_FILL`、`WRITE_HIT_THROUGH`、`WRITE_HIT_BACK`、`WRITE_MISS_ALLOCATE_THROUGH`、`WRITE_MISS_ALLOCATE_BACK`、`WRITE_MISS_BYPASS`。没有 UNKNOWN/OTHER；dirty eviction 是附带事件。

Trace parser 接受逐行或逗号分隔的 `R 0`、`W 4`、`R 0x10`、`W 0x20`，接受小写操作符和 `R:0` / `W:0x10`；空文本为正式空 trace。裸地址、未知操作、缺少或非法地址、负地址、额外字段以及连续逗号产生的空项均拒绝。

`WritePolicyController` 驱动 Session，`WritePolicyPageState` 与 immutable View Models 向 GUI 提供 decision、traffic、cache、statistics、timeline 和 comparison。选择历史 step 只改变 selected index/step/decisions 与 timeline 标记，不改变 latest/next/completion、current Cache、statistics、final dirty state、divergence counts 或 comparison summary。页面提示为：`Viewing historical evidence; cache and statistics remain at the latest run state.`

## Traffic 模型

`WriteTrafficAssumptions.store_size_bytes` 必须是正整数、不大于 block size，store 不得跨 block。模型不支持 partial dirty-byte mask，也不拆分跨 block write。

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

所有 lower-memory traffic 都是教学分析值，不是宿主机真实 I/O。

运行结束时 `final_dirty_lines` 是仍 valid 且 dirty 的 resident line 数；`final_dirty_bytes = final_dirty_lines × block_size_bytes`，`memory_write_bytes_with_final_drain = memory_write_bytes + final_dirty_bytes`，`total_lower_memory_bytes_with_final_drain = total_lower_memory_bytes + final_dirty_bytes`。Final drain 不属于 trace step、不调用 flush、不修改 Cache，也不重复计算已经 eviction 写回的 line；runtime 与 including-final-drain 分开显示。

## 不变量与 divergence

每条 lane 验证：

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

比较层验证 `all_outcomes_agree_steps + outcome_divergence_steps = accesses`。

七类 divergence 为：HIT/MISS outcome、allocated、bypassed、当前步骤 dirty writeback、当前步骤 lower-memory total bytes、每个位置的 valid/dirty，以及完整 snapshot 的 valid/tag/dirty/last_used/insert_time。Dirty-state divergence 与 full cache-state divergence 不同；full state 也不只比较 tag 集合。

## 七个教学 Preset 的稳定结果

| Preset | Trace | Runtime bytes（WT+WA / WT+NWA / WB+WA / WB+NWA） | With drain bytes | 关键结果 |
|---|---|---:|---:|---|
| Read-Only Control | `R 0, R 0, R 16, R 0` | 32 / 32 / 32 / 32 | 32 / 32 / 32 / 32 | 四 lane 均 2H/2M，无 dirty；无 write 时行为与流量相同。 |
| Repeated Writes to Resident Line | `R 0, W 0, W 0, W 0, W 0, W 0` | 36 / 36 / 16 / 16 | 36 / 36 / 32 / 32 | WA/NWA 不影响 resident hit；WT 立即写，WB 合并 writes 但留下 final dirty data。 |
| Write Miss Allocate vs Bypass | `W 0, R 0` | 20 / 20 / 16 / 20 | 20 / 20 / 32 / 20 | WA 使后续 read hit；NWA 首次 bypass，后续 read 仍 miss。 |
| Dirty Eviction | `W 0, W 16` | 40 / 8 / 48 / 8 | 40 / 8 / 64 / 8 | WT victim clean；WB+WA dirty victim 产生整 block write-back。 |
| Streaming Stores | `W 0, W 16, W 32, W 48` | 80 / 16 / 112 / 16 | 80 / 16 / 128 / 16 | 此无复用 trace 中 NWA 避免 fill；不代表 NWA 普遍最优。 |
| Read-After-Write Reuse | `W 0, R 0, R 0` | 20 / 20 / 16 / 20 | 20 / 20 / 32 / 20 | WA 为 2H/1M，NWA 为 1H/2M；WA 保留 block 供 read 复用。 |
| Mixed Dirty Conflict | `W 0, W 16, R 0, W 32, R 16` | 76 / 44 / 96 / 44 | 76 / 44 / 112 / 44 | Outcome/Allocation/Bypass/Writeback/Traffic/Dirty State/Cache State divergence = 1/4/3/2/5/5/5。 |

Mixed Dirty Conflict 说明同一 trace 可同时产生 future outcome、allocation、bypass、dirty-state、dirty writeback、traffic 与 full cache-state divergence。

## GUI 与平台

页面包含 Experiment Controls、Teaching Summary、Current Access and Run Position、Divergence Summary、Selected Historical Decision Cards、Current Four-Lane Cache State、Runtime / Final Drain Traffic Comparison、Current Cumulative Statistics、Timeline 和 Policy Comparison Summary。整体使用纵向 `QScrollArea`，四 Cache 为 2×2；宽表格和 timeline 可横向滚动。Traffic Canvas 使用 QWidget + QPainter，未引入 matplotlib、numpy、pandas 或 QtCharts；图形旁提供精确数字，状态不只依赖颜色。

Comparison Summary 支持 runtime lowest-traffic、with-drain lowest-traffic、highest-hit-rate、tie、runtime/drain leader 一致性、allocation/future outcome、propagation/dirty state、propagation/runtime traffic、dirty eviction、bypass、actual observations 与 caution。固定 caution：`Results apply only to the current trace, cache configuration, and traffic assumptions.`

平台为 Learn 6 个加 Classic Tools 2 个，共 8 Available、0 Coming Soon。Write Policy 首次导航由 Registry factory 延迟创建，再次导航复用实例；切换页面后 experiment、timeline、selection、Cache 和 statistics 保持。Main Window 没有 Write Policy 专用 if/elif。

## 验证记录

- 720/720 项 `unittest` 通过，Skip 0。
- Qt offscreen smoke 与七个 preset GUI smoke 通过。
- 平台 8 Available / 0 Coming Soon、lazy navigation、实例复用和状态保持通过。
- 真实 GUI 入口运行超过 3 秒，无 traceback 或崩溃。
- 环境出现非致命 `QFontDatabase` 字体目录警告；实际字体和界面显示正常。
- 用户已完成人工视觉验收并确认通过。
