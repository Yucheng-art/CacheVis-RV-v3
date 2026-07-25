# 项目交接上下文

## 仓库关系

- V1：`D:\Projects\SoftCopyright\CacheVis-RV`，软件著作权归档版，只读。
- V2：`D:\Projects\CacheVis-RV-v2`，稳定 Address Visualizer 版，只读。
- V3：`D:\Projects\CacheVis-RV-v3`，多 Lab 平台版，独立仓库。

V3 不继承 V1/V2 的 Git 历史。本初始化任务不复制 V2 源码，也不修改 V1/V2。

## 当前状态

仓库当前只包含项目管理和规划文档，没有业务代码、依赖环境、构建产物或已实现的 Lab。

## 后续接手顺序

1. 阅读根目录 `AGENTS.md`。
2. 阅读产品与技术架构、V2 继承计划、路线图和决策记录。
3. 在开始业务开发前明确首个 Lab 的范围与验收标准。
4. 按“纯逻辑 → `unittest` → GUI”的顺序实施。
5. 仅在获得明确许可后执行提交、推送、创建 tag 或 PR。

## 禁止事项

不得修改 V1/V2，不得复制其环境、缓存、PDF、构建输出或 Git 元数据，不得把规划内容表述为已完成功能。
