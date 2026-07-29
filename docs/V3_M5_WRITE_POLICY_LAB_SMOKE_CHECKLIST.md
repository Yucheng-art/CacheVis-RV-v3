# V3 M5 Write Policy Lab Smoke Checklist

本清单用于重复验证 M5 稳定基线。自动化结果不能代替后续发布候选的人工视觉检查。

## 1. 自动回归

在仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

验收：

- `Ran 720 tests`
- `OK`
- Skip 0
- 不修改、删除、跳过或弱化测试

## 2. 平台与导航

- [ ] Home 精确显示 8 个 Available Lab、0 个 Coming Soon。
- [ ] Learn 顺序为 Address Explorer、Miss Type、Locality、Policy、Performance、Write Policy。
- [ ] Classic Tools 顺序为 Single Experiment、Compare Experiment。
- [ ] Sidebar 不显示空 Coming Soon group。
- [ ] Write Policy 可从 Home 与 Sidebar 打开。
- [ ] 其余七个 Lab 仍可导航。
- [ ] 首次导航延迟创建 Write Policy 页面。
- [ ] 再次导航复用同一页面实例。
- [ ] 页面切换后 experiment、timeline、selection、Cache 与 statistics 保持。
- [ ] Main Window 不含 Write Policy 专用 if/elif。

## 3. 基本交互与状态

- [ ] `WritePolicyLabWidget` 可在 offscreen Qt 环境创建。
- [ ] 七个 preset 均可填充，切换 preset 不自动 Load。
- [ ] R/W trace 支持逐行、逗号、小写和冒号格式，错误输入有明确提示。
- [ ] Load 后四 lane 都是冷 Cache。
- [ ] Step 每次只推进一个 access；Run All 只运行剩余步骤。
- [ ] 默认 latest 与 selected 一致。
- [ ] 选择历史 step 后 selected/latest 分离。
- [ ] 历史选择不改变 current Cache、statistics、next index 或 final dirty state。
- [ ] 历史模式显示 `Viewing historical evidence; cache and statistics remain at the latest run state.`
- [ ] 新 Step 自动选择 latest。
- [ ] Reset 保留实验输入并恢复冷状态；Clear 恢复空 Page State。

## 4. Decision、Cache 与 Traffic

- [ ] 四 lane 固定顺序为 WT+WA、WT+NWA、WB+WA、WB+NWA。
- [ ] HIT/MISS、decision kind、allocation、bypass、dirty before/after 清楚显示。
- [ ] clean/dirty eviction 使用 `evicted_way`，invalid fill/bypass 不误报 victim。
- [ ] 四 lane Cache 使用 2×2，INVALID/CLEAN/DIRTY 可辨识且不只依赖颜色。
- [ ] 当前 step 的 block fill、immediate store、bypass、dirty write-back 清楚显示。
- [ ] Runtime 与 Final Dirty Drain 分离，图形与精确数字一致。
- [ ] Cumulative Statistics 与八项页面 invariants 正常。
- [ ] Timeline 可横向滚动，selected 与 latest 可独立。
- [ ] Expected Teaching Conclusion 与 Actual Observations 视觉区分明确。
- [ ] Comparison leaders 支持 tie，并显示固定 caution。

## 5. 七个 Preset 精确结果

所有数字单位均为 lower-memory bytes，顺序均为 WT+WA / WT+NWA / WB+WA / WB+NWA。

| Preset | Trace | Runtime | Including final drain | 额外验收 |
|---|---|---:|---:|---|
| Read-Only Control | `R 0, R 0, R 16, R 0` | 32 / 32 / 32 / 32 | 32 / 32 / 32 / 32 | 四 lane 2H/2M，无 dirty。 |
| Repeated Writes to Resident Line | `R 0, W 0, W 0, W 0, W 0, W 0` | 36 / 36 / 16 / 16 | 36 / 36 / 32 / 32 | WT immediate writes；WB final dirty。 |
| Write Miss Allocate vs Bypass | `W 0, R 0` | 20 / 20 / 16 / 20 | 20 / 20 / 32 / 20 | WA 后续 read hit；NWA 首次 bypass。 |
| Dirty Eviction | `W 0, W 16` | 40 / 8 / 48 / 8 | 40 / 8 / 64 / 8 | WB+WA 发生整 block dirty write-back。 |
| Streaming Stores | `W 0, W 16, W 32, W 48` | 80 / 16 / 112 / 16 | 80 / 16 / 128 / 16 | 当前无复用 trace 中 NWA 避免 fills。 |
| Read-After-Write Reuse | `W 0, R 0, R 0` | 20 / 20 / 16 / 20 | 20 / 20 / 32 / 20 | WA 2H/1M；NWA 1H/2M。 |
| Mixed Dirty Conflict | `W 0, W 16, R 0, W 32, R 16` | 76 / 44 / 96 / 44 | 76 / 44 / 112 / 44 | divergence 精确为 1/4/3/2/5/5/5。 |

Mixed divergence 顺序为 Outcome / Allocation / Bypass / Writeback / Traffic / Dirty State / Cache State。

## 6. Qt 与真实入口

- [ ] Offscreen 创建窗口、导航、Step、Run All、Reset、Clear 均无异常。
- [ ] 页面整体纵向滚动、小窗口布局、宽表格和 Timeline 横向滚动正常。
- [ ] 浅色区域文字对比度清晰。
- [ ] 真实 GUI 入口进入 Qt event loop 至少 3 秒，无 traceback 或崩溃。
- [ ] 若出现 `.venv/Lib/site-packages/PySide6/lib/fonts` 的 `QFontDatabase` 警告，仅在实际字体和界面显示正常时作为非致命环境警告记录。

## 7. M5 封版记录

- 自动测试：720/720 通过，Skip 0。
- Qt offscreen：通过。
- 七 preset GUI smoke：通过。
- 平台 8 Available / 0 Coming Soon：通过。
- Lazy navigation、实例复用与状态保持：通过。
- 真实 GUI：运行超过 3 秒，无 traceback。
- 用户人工视觉验收：已确认通过。

固定教学提示：`Results apply only to the current trace, cache configuration, and traffic assumptions.` 不得将当前 trace 的最低流量 lane 宣称为普遍最优策略。
