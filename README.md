# CacheVis-RV V3

CacheVis-RV V3 是面向计算机组成与 RISC-V Cache 教学的多实验室交互式可视化平台。

V3 已完成 M0 平台基线：在保持 V2 稳定行为的基础上，建立了模块化核心、独立 Lab 包和多 Lab 平台外壳。当前应用身份为 `CacheVis-RV V3.0`。

## 版本定位

- V1：软件著作权归档版，仅作只读参考。
- V2：稳定的 Address Visualizer 版，仅作只读参考。
- V3：采用 Sidebar、Home、Lab Registry 与 `QStackedWidget` 的多 Lab 平台版。

## 当前可用功能

- Address Explorer
- Single Experiment
- Compare Experiment

以下教学 Lab 仍为 Coming Soon，尚未实现：

- Miss Type Lab
- Locality Lab
- Policy Lab
- Performance Lab
- Write Policy Lab

平台页面按需创建并缓存，切换页面不会丢失已创建 Lab 的状态。当前 M0 回归基线为 169 项 `unittest` 全部通过。

下一阶段为 M1 Miss Type Lab，继续遵循“纯逻辑 → `unittest` → GUI”的开发顺序。

## 文档

- [产品与技术架构](docs/V3_PRODUCT_AND_TECH_ARCHITECTURE.md)
- [M0 平台外壳总结](docs/V3_M0_PLATFORM_SHELL_SUMMARY.md)
- [M0 Smoke Checklist](docs/V3_M0_SMOKE_CHECKLIST.md)
- [项目交接上下文](docs/PROJECT_HANDOFF_CONTEXT.md)
- [V2 继承计划](docs/V2_INHERITANCE_PLAN.md)
- [路线图](docs/ROADMAP.md)
- [决策记录](docs/DECISIONS.md)

## 仓库约束

V1/V2 始终只读。不得上传 `Cache*.pdf`、环境目录、缓存或构建输出；未经明确许可不得提交、推送、创建 tag 或 PR。
