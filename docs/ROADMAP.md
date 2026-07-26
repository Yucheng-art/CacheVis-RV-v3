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

## M3：Policy Lab（下一阶段）

- 按“纯逻辑 → `unittest` → GUI”顺序研究和展示 replacement policy 行为。
- 当前尚未实现，不在 M2 文档中声明任何功能行为。

## 后续 Lab

- Performance Lab
- Write Policy Lab

上述 Lab 当前均为规划项，尚未实现。

当前仍未实现 Policy、Performance、Write Policy、L2、历史 Cache snapshot 回滚、动画、Locality 双实验同时对比引擎和报告导出扩展。

## 持续质量要求

- 每个 Lab 独立分层和测试。
- 纯逻辑不得依赖 PySide6。
- 保持 V1/V2 只读。
- 排除环境目录、缓存、`Cache*.pdf`、`outputs`、`build` 和 `dist`。
- 发布、tag 和远程操作必须获得明确许可。
