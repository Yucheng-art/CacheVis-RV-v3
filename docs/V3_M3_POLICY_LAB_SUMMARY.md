# V3 M3 Policy Lab 总结

## 里程碑结果

M3 已完成 replacement policy 同步比较核心、Controller/View Models、独立 PySide6 页面和平台接入。Policy Lab 已从 Coming Soon 迁移为 Available，可从 Home 与 Sidebar 打开；Registry factory 延迟创建页面，Main Window 使用通用 lazy page cache 缓存并复用页面实例。

M3 完成时共有 477 项 `unittest` 全部通过，无 skip；Qt offscreen smoke、真实 GUI 入口启动以及用户人工视觉验收均已通过。

## 同步比较模型

Policy Lab 对三条独立 lane 同步执行同一 address trace：

- LRU
- FIFO
- seeded Random

三条 lane 使用相同的 Cache size、block size、ways、address width 与 address trace，唯一变化为 replacement policy。实现直接使用 core 的正式字符串接口 `LRU`、`FIFO`、`Random`；项目当前没有正式 `ReplacementPolicy` enum，因此没有创建重复枚举。

## 三种正式决策

- `HIT`：目标 tag 已位于映射 set，不 fill、不 eviction。
- `INVALID_FILL`：目标 tag 不在 set，但存在 invalid way；填充空 way，不驱逐有效 Cache line，也不属于 replacement。
- `EVICTION`：目标 tag 不在 set 且 set 已满；只有此时 replacement policy 才选择 victim。

策略证据：

- LRU 根据 `last_used` 选择最久未使用候选；hit 会更新 recency。
- FIFO 根据 `insert_time` 选择最早插入候选；hit 不刷新 insertion order。
- Random 将所有 valid ways 视为候选并执行 seeded replay；Random 不代表最优、最旧或最少使用。

## Random 可复现与隔离

Session 持有独立的 `random.Random(seed)` 状态。每次 Random access：

1. 保存进程模块级 random 状态。
2. 临时载入 Session 私有随机状态。
3. 正式调用一次 `CacheSimulator.access`。
4. 保存更新后的 Session 私有随机状态与 draw index。
5. 在 `finally` 中恢复进程原有的全局 random 状态。

该机制不修改 core、不调用未恢复的全局 `random.seed`，也不复制 Random victim 算法。

## Divergence 与教学因果链

Policy Lab 分别记录：

- victim divergence
- state divergence
- outcome divergence

victim/state divergence 可以先发生，而三条 lane 当前的 HIT/MISS 仍完全相同；后续访问才可能产生 outcome divergence。

```text
Same address
→ Same set and tag
→ Each policy observes its own Cache state
→ HIT / INVALID FILL / EVICTION
→ Victim selection
→ Cache state divergence
→ Possible future HIT/MISS divergence
```

## 页面与历史选择语义

页面包含：

- Experiment Controls
- Preset Teaching Insight
- Current Access
- Divergence Summary
- Selected Decision Evidence
- Latest Cache State
- Statistics Comparison
- Timeline

历史 Timeline 选择只更新：

- `selected_step`
- Selected Decision Evidence
- Timeline SELECTED

历史选择不回滚或推进：

- Current Access
- LRU/FIFO/Random Cache state
- Statistics
- Divergence Summary
- Random stream
- `next_step_index`

## 七个内置 Preset

| Preset | LRU | FIFO | Random | 教学重点 |
|---|---:|---:|---:|---|
| No Replacement Pressure | 2H / 2M | 2H / 2M | 2H / 2M | invalid way 可用时不发生 eviction divergence |
| Victim Divergence Before Outcome | 1H / 3M | 1H / 3M | 1H / 3M | 第四步 outcome 相同，但 LRU/FIFO victim 不同，state 已分叉 |
| LRU Advantage | 2H / 3M | 1H / 4M | 1H / 4M | state divergence step 3，outcome divergence step 4，lag=1 |
| FIFO Advantage | 1H / 4M | 2H / 3M | 2H / 3M | state step 3、outcome step 4、lag=1；LRU 并非对每个有限 trace 都更优 |
| Set-Local Pressure | 1H / 4M | 2H / 3M | 2H / 3M | replacement 只在目标 set 内发生，其他 set 可保持空闲 |
| Direct-Mapped Control | 0H / 4M | 0H / 4M | 0H / 4M | 每个 set 只有一个 way，没有 victim 选择自由 |
| Seeded Random Replay | 0H / 8M | 0H / 8M | 0H / 8M | 相同 seed 与 trace 可复现 Random lane，不比较普遍优劣 |

## Statistics 与不变量

每条 policy lane 记录：

- accesses
- hits
- misses
- invalid fills
- evictions
- hit rate
- miss rate

比较层记录：

- all-agree steps
- outcome divergence steps
- victim divergence steps
- state divergence steps

持续验证：

- `Hits + Misses = Accesses`
- `Invalid Fills + Evictions = Misses`
- `All Agree + Outcome Divergence = Accesses`

current trace leader 只描述当前有限 trace，不代表策略普遍最优。

## 尚未实现

- Performance Lab
- Write Policy Lab
- L2
- write-back 完整教学实验
- 动画
- 历史 Cache snapshot 回滚
- 多 trace 批量策略排名
- 报告导出扩展

下一阶段为 M4 Performance Lab。
