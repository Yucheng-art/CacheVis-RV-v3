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

## M2：Locality Lab（下一阶段）

- 先定义 temporal locality 与 spatial locality 的纯逻辑教学模型。
- 再建立 `unittest` 验证。
- 最后设计独立 controller、view model 和 widget，并接入平台。

## 后续 Lab

- Policy Lab
- Performance Lab
- Write Policy Lab

上述 Lab 当前均为规划项，尚未实现。

M2 Locality Lab 也尚未实现；本路线图仅记录下一阶段方向。

## 持续质量要求

- 每个 Lab 独立分层和测试。
- 纯逻辑不得依赖 PySide6。
- 保持 V1/V2 只读。
- 排除环境目录、缓存、`Cache*.pdf`、`outputs`、`build` 和 `dist`。
- 发布、tag 和远程操作必须获得明确许可。
