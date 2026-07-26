# V3 M4 Performance Lab Smoke Checklist

## 自动验证

- [x] 620 项 `unittest` 全部通过，无 skip。
- [x] `PerformanceLabWidget` 可在 Qt offscreen 环境创建。
- [x] 六个 sweep preset 均可填充和运行。
- [x] 默认 selected point 为 baseline，默认 chart metric 为 AMAT。
- [x] 七种 metric 均可切换且不重新运行 sweep。
- [x] 表格选择更新 selected point，但不重跑 sweep。
- [x] best/tie、comparison 与 `SweepResult` 不因选择改变。
- [x] Capacity Knee 的 16B/32B best AMAT tie 正确。
- [x] Associativity 的 2-way/4-way tie 正确。
- [x] Hit Rate Is Not AMAT reversal 正确。
- [x] 空 trace 的 AMAT、bytes/access、stall fraction 与 speedup 为 N/A。
- [x] 图表可处理 N/A、单 point 和相同 x。
- [x] Load Example 只填充输入，不自动分析。
- [x] Analytical L1/L2 Example 得到 AMAT 3.8。
- [x] probability outcomes 与 contributions 不变量正确。
- [x] Sweep 与 Hierarchy 相互独立并可分别清理。
- [x] Home 与 Sidebar 可进入 Performance Lab。
- [x] Registry factory 延迟创建，Main Window 复用同一实例并保持状态。
- [x] Write Policy 保持 Coming Soon，不创建页面。
- [x] 真实 GUI 入口进入事件循环至少 3 秒，无 traceback。

## 用户人工视觉验收

用户已确认以下项目通过：

- [x] Home Performance 卡片与 Sidebar Learn 顺序。
- [x] 页面整体布局、纵向滚动与第二次启动。
- [x] Point Editor 和比较表横向滚动。
- [x] 六个 sweep preset。
- [x] Restore Preset、Run Sweep、Clear Sweep。
- [x] Expected Teaching Conclusion 与 Actual Observations 的区分。
- [x] Capacity Knee 与 Associativity tie。
- [x] Sequential / Stride 对比。
- [x] Miss Penalty Sensitivity。
- [x] Hit Rate Is Not AMAT reversal。
- [x] 七种图表指标及 baseline / selected / best 标记。
- [x] Sweep Point Table 与 Selected Point Detail。
- [x] 四项 performance invariants。
- [x] Analytical L1/L2 输入、概率、cycle contributions 和 AMAT 3.8。
- [x] L2 local/global miss rate 解释和 limitation notes。
- [x] Sweep/Hierarchy 独立运行与清理。
- [x] 页面切换后的实例和状态保持。
- [x] 未发现明显布局、滚动、配色、裁切或文字对比度问题。

## 稳定结果

| Preset | 稳定结果 |
|---|---|
| Capacity Knee | 8B 0H/16M AMAT 23；16B 与 32B 均 12H/4M AMAT 6.5 |
| Sequential Block Benefit | block 4/8/16 的 AMAT 为 23/13/8 |
| Stride Block Cost | block 4/8/16 均 0H/4M，AMAT 为 23/25/29 |
| Associativity Conflict Relief | 1-way AMAT 23；2-way/4-way 均约 8.3333 |
| Miss Penalty Sensitivity | 相同 2H/2M；overhead 10/50/100 的 AMAT 为 6/26/51 |
| Hit Rate Is Not AMAT | Fast Small hit rate 0、AMAT 11；Slow Large hit rate 0.5、AMAT 13 |

本清单记录 M4 已验证状态，不表示 Write Policy Lab、实际 L2 Cache hierarchy simulator、inclusion/exclusion、write-back traffic、parallel lookup、pipeline CPI、energy model、hardware-derived hit-time model、animation 或 performance report export 已实现。
