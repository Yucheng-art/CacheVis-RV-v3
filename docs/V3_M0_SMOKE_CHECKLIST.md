# V3 M0 Smoke Checklist

## 自动验证

- [x] 169 项 `unittest` 全部通过，无 skip。
- [x] CLI 单实验可运行。
- [x] CLI Compare 可运行。
- [x] `CacheVisMainWindow` 可创建。
- [x] 窗口标题为 `CacheVis-RV V3.0`。
- [x] 真实 GUI 入口进入 Qt event loop 且无 traceback。
- [x] Home 为默认页面。
- [x] Address Explorer、Single Experiment、Compare Experiment 可按需创建。
- [x] 已创建页面可缓存复用。
- [x] Coming Soon Lab 不会创建空白页面。

## 人工验收记录

- [x] V3 Platform Shell 整体视觉验收通过。
- [x] Sidebar 与 Home 信息层级可读。
- [x] Address Explorer 的 Tag / Index / Offset 区域文字清晰。
- [x] Structured Explanation 浅色卡片文字清晰。
- [x] Cache Contents 元数据与状态标签清晰。
- [x] Timeline 的 Step、地址、结果和状态标签清晰。

## 后续回归要求

- 平台导航不得重置已缓存 Lab 状态。
- Coming Soon Lab 不得提前标记为 Available。
- 平台 Theme 不得覆盖 Lab 内部语义颜色。
- 新 Lab 必须先完成纯逻辑和 `unittest`，再接入 GUI。
