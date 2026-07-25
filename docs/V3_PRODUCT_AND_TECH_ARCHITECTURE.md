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
- Single Experiment
- Compare Experiment

仍为 Coming Soon：

- Locality Lab
- Policy Lab
- Performance Lab
- Write Policy Lab

Coming Soon 仅表示规划状态，不代表已有业务实现。

## 分层架构

V3 继续采用 Python、PySide6 和 `unittest`。当前代码按以下边界组织：

1. `cachevis_rv.core`：Cache 配置、行、模拟器、替换策略和统计。
2. 实验服务包：trace、runner 与 report 等可复用纯逻辑服务。
3. 独立 Lab：Address Explorer、Miss Type Lab、Single Experiment、Compare Experiment 分别拥有自己的逻辑、controller/view model 与 widget 边界。
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

## 当前质量基线

- 270 项 `unittest` 全部通过，无 skip。
- M0 的 CLI、GUI、页面懒加载和 V2 兼容行为继续由回归测试覆盖。
- Miss Type Lab 的三组 preset、双 Cache、Evidence、Statistics、Timeline 和页面状态保持已完成 smoke 与人工视觉验收。

下一阶段为 M2 Locality Lab，仍按“纯逻辑 → `unittest` → GUI”的顺序推进。
