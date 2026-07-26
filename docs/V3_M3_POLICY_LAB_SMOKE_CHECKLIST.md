# V3 M3 Policy Lab Smoke Checklist

## 自动验证

- [x] 477 项 `unittest` 全部通过，无 skip。
- [x] `PolicyLabWidget` 可在 Qt offscreen 环境创建。
- [x] 七个 preset 参数与稳定结果正确。
- [x] Reset、Step、Run All 与整数 Random seed 正常。
- [x] LRU、FIFO、Random 使用同一配置和 trace 同步运行。
- [x] HIT、INVALID FILL、EVICTION 证据正确。
- [x] LRU 显示 `last_used` 与 LRU→MRU 顺序。
- [x] FIFO 显示 `insert_time` 与 oldest→newest 顺序，hit 不刷新 insertion order。
- [x] Random 显示 candidates、seed、draw index，并可 seeded replay。
- [x] victim、state、outcome divergence 与 lag 正确。
- [x] 历史选择只更新 Selected Decision Evidence 和 Timeline SELECTED。
- [x] Current Access、三条 Cache、Statistics、Divergence Summary 不因历史选择回滚。
- [x] 历史选择不推进 Random draw 或 `next_step_index`。
- [x] 继续 Step 后最新步骤恢复为 CURRENT/SELECTED。
- [x] Home 与 Sidebar 可以进入 Policy Lab。
- [x] Registry factory 延迟创建页面。
- [x] 切换到 Locality/Miss Type 后返回时复用同一实例并保持状态。
- [x] Performance 与 Write Policy 不创建页面。
- [x] 真实 GUI 入口进入事件循环至少 3 秒，无 traceback。

## 用户人工视觉验收

用户已确认以下项目通过：

- [x] Home 与 Sidebar 导航。
- [x] 页面整体布局与滚动。
- [x] LRU、FIFO、Random 三条 lane 可读。
- [x] 七个 preset。
- [x] Reset、Step、Run All 与 Random seed。
- [x] Current Access 与 Selected Decision 的区分。
- [x] HIT、INVALID FILL、EVICTION 表达。
- [x] LRU `last_used` 与顺序。
- [x] FIFO `insert_time` 与顺序。
- [x] Random candidates、seed 与 draw index。
- [x] 三条 Cache lane 和状态标记。
- [x] Divergence Summary。
- [x] Victim → State → Outcome 因果链。
- [x] LRU Advantage、FIFO Advantage 与 Direct-Mapped。
- [x] Statistics 与 Timeline。
- [x] 历史选择不回滚最新状态。
- [x] 页面切换后的状态保持。
- [x] 未发现明显布局、滚动、配色或文字对比度问题。

## 稳定结果

| Preset | LRU | FIFO | Random |
|---|---:|---:|---:|
| No Replacement Pressure | 2H / 2M | 2H / 2M | 2H / 2M |
| Victim Divergence Before Outcome | 1H / 3M | 1H / 3M | 1H / 3M |
| LRU Advantage | 2H / 3M | 1H / 4M | 1H / 4M |
| FIFO Advantage | 1H / 4M | 2H / 3M | 2H / 3M |
| Set-Local Pressure | 1H / 4M | 2H / 3M | 2H / 3M |
| Direct-Mapped Control | 0H / 4M | 0H / 4M | 0H / 4M |
| Seeded Random Replay | 0H / 8M | 0H / 8M | 0H / 8M |

本清单记录 M3 已验证状态，不表示 Performance Lab、Write Policy Lab、L2、write-back 完整教学实验、动画、历史 Cache snapshot 回滚、多 trace 批量策略排名或报告导出扩展已经实现。
