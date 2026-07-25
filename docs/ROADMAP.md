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

## M1：Miss Type Lab

1. M1.1：实现纯 Python 的严格 3C Miss 分类核心及测试。
2. 后续阶段：定义 controller、view model 和教学交互。
3. 最后接入独立 Miss Type Widget 与平台导航。

在 GUI 阶段完成前，Miss Type Lab 必须保持 Coming Soon，且不得配置 widget factory。

## 后续 Lab

- Locality Lab
- Policy Lab
- Performance Lab
- Write Policy Lab

上述 Lab 当前均为规划项，尚未实现。

## 持续质量要求

- 每个 Lab 独立分层和测试。
- 纯逻辑不得依赖 PySide6。
- 保持 V1/V2 只读。
- 排除环境目录、缓存、`Cache*.pdf`、`outputs`、`build` 和 `dist`。
- 发布、tag 和远程操作必须获得明确许可。
