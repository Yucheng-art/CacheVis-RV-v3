# V3 M0 Platform Shell 总结

## 完成范围

M0 已建立与 V2 行为兼容的 V3 多 Lab 基线：

- V2 稳定运行时基线导入。
- Cache core package 提取。
- 实验服务 packages 提取。
- Address Explorer package 与 controller 提取。
- Single Experiment、Compare Experiment 独立 Lab 化。
- Sidebar、Home、Lab Registry 与 `QStackedWidget` 平台外壳。
- Address Explorer 浅色语义区域可读性修正。
- 应用身份更新为 `CacheVis-RV V3.0`。

## 平台行为

- 启动后默认显示 Home。
- Address Explorer、Single Experiment、Compare Experiment 当前可用。
- 可用页面首次访问时创建，之后缓存复用。
- 在页面间切换不会丢失已创建页面的状态。
- Miss Type、Locality、Policy、Performance、Write Policy Lab 仍为 Coming Soon，未提供 factory。

## 验证基线

- 169 项 `unittest` 全部通过，无 skip。
- CLI 单实验和 Compare smoke 通过。
- GUI 真实入口进入 Qt event loop，无 traceback。
- V3 Platform Shell 已完成人工视觉验收。

## 下一阶段

下一阶段是 M1 Miss Type Lab。M1.1 仅实现严格 3C Miss 分类纯逻辑内核，不提前实现 GUI，也不改变 Registry 的 Coming Soon 状态。

## 保留约束

- V1/V2 只读。
- 不上传 `Cache*.pdf`、环境目录、缓存或构建输出。
- 每个 Lab 保持独立 controller、view model 和 widget。
