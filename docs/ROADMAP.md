# 路线图

## M0：V3 稳定平台基线（已完成）

- 导入 V2 稳定运行时基线。
- 提取 `cachevis_rv.core` 核心 package，并保留扁平兼容 facade。
- 提取实验服务 packages。
- 提取 Address Explorer package 与 controller。
- 将 Single Experiment 和 Compare Experiment 独立为 Classic Labs。
- 建立 Sidebar、Home、Lab Registry 与 `QStackedWidget` 平台外壳。
- 实现可用页面的 lazy initialization 与状态缓存。
- 完成 V3.0 应用身份和 Address Explorer 视觉可读性修正。
- 建立 169 项测试的 M0 回归基线。

## M1：Miss Type Lab（已完成）

1. M1.1：实现纯 Python 的严格 3C Miss 分类核心及测试。
2. M1.2：实现 controller、Page State、Cache 与 Evidence view model。
3. M1.3：实现独立 Miss Type Widget，并接入 Home、Sidebar、Registry 和 Main Window 页面缓存。

- 分类单位为 memory block。
- Reference Cache 使用同容量、同 block size、fully associative、LRU 配置。
- Actual Cache 在基础 3C Lab 中固定使用 LRU。
- 页面展示 Actual/Reference Cache、Evidence、Statistics 和 Timeline。
- 历史 Timeline 选择不回滚 Cache 或累计 Statistics。
- 三个内置 preset 结果为 C C C C、C C F F、C C C A。
- Miss Type Lab 当前状态为 Available。
- M1 完成时回归基线为 270 项测试。

## M2：Locality Lab（已完成）

1. M2.1：实现纯 Python Locality Analyzer、Session、统计、不变量和六个教学 preset。
2. M2.2：实现 Controller、Page State、Cache/Evidence/Statistics/Timeline/Block Access view model。
3. M2.3：实现独立 Locality Widget，并接入 Home、Sidebar、Registry 和 Main Window 页面缓存。

- 主证据分类为 First Touch、Spatial、Temporal。
- 展示 address/block reuse gap、block reuse distance、same-block transition 和 address delta。
- 展示 Cache State、Block/Offset Access Map、Statistics、Teaching Insight 和 Timeline。
- 历史 Timeline 选择不回滚 Current Access、Cache、Statistics 或 Block Map。
- Row-major/Column-major 教学对比明确区分 locality 潜力与实际 Cache 利用效果。
- Locality Lab 当前状态为 Available。
- M2 完成时回归基线为 370 项测试，Qt smoke 与用户人工视觉验收通过。

## M3：Policy Lab（已完成）

1. M3.1：实现纯 Python 的 replacement policy 同步比较核心、决策证据、独立 seeded Random stream 和七个教学 preset。
2. M3.2：实现 Controller、Page State、Cache/Decision/Statistics/Timeline/Divergence view model。
3. M3.3：实现独立 Policy Widget，并接入 Home、Sidebar、Registry 和 Main Window 页面缓存。

- 同一配置与 trace 同步比较 LRU、FIFO 和 seeded Random。
- 正式区分 HIT、INVALID_FILL 和 EVICTION；只有 full-set miss 才触发 replacement。
- 展示 last_used、insert_time、Random candidates、victim/state/outcome divergence 和完整因果链。
- 历史 Timeline 选择只更新 Selected Decision Evidence，不回滚最新 Cache、Statistics、Divergence 或 Random stream。
- 七个 preset 覆盖无替换压力、victim 先于 outcome 分叉、LRU/FIFO 有限 trace 优势、set-local pressure、direct-mapped control 和 seeded replay。
- Policy Lab 当前状态为 Available。
- M3 完成时回归基线为 477 项测试，Qt smoke、真实 GUI 启动与用户人工视觉验收通过。

## M4：Performance Lab（已完成）

1. M4.1：实现显式 timing、单级 performance runner、sweep、analytical L1/L2 和教学 preset。
2. M4.2：实现 Controller、Page State、metrics/sweep/chart/comparison/hierarchy view model。
3. M4.3：实现独立 Performance Widget，并接入 Home、Sidebar、Registry 和 Main Window page cache。

- 六个 sweep 覆盖 capacity knee、block benefit/cost、associativity、miss penalty 和 Hit Rate/AMAT reversal。
- 页面提供可编辑 Point Editor、七指标 QPainter 图表、比较表、selected point、tradeoff 与 analytical L1/L2 分解。
- 选择 point 或 chart metric 不重新运行 sweep；sweep 与 hierarchy 独立运行和清理。
- Performance Lab 当前状态为 Available。
- M4 完成时回归基线为 620 项测试，Qt smoke、真实 GUI 启动和用户人工视觉验收通过。

## M5：Write Policy Lab（下一阶段）

- Write Policy Lab 当前仍为 Coming Soon，`factory=None`。
- 继续遵循“纯逻辑 → `unittest` → GUI”的开发顺序。

当前仍未实现实际 L2 Cache hierarchy simulator、inclusion/exclusion、write-back traffic、parallel lookup、pipeline CPI、energy model、hardware-derived hit-time model、动画和 performance report export。

## 持续质量要求

- 每个 Lab 独立分层和测试。
- 纯逻辑不得依赖 PySide6。
- 保持 V1/V2 只读。
- 排除环境目录、缓存、`Cache*.pdf`、`outputs`、`build` 和 `dist`。
- 发布、tag 和远程操作必须获得明确许可。
