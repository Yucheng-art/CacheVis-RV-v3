# CacheVis-RV V3 协作约束

## 仓库边界

- V1 位于 `D:\Projects\SoftCopyright\CacheVis-RV`，是软件著作权归档版，只能只读参考。
- V2 位于 `D:\Projects\CacheVis-RV-v2`，是稳定 Address Visualizer 版，只能只读参考。
- 不得修改、提交或改变 V1/V2 的 Git 状态。
- 未经用户明确许可，不得执行 `commit`、`push`、创建 `tag` 或创建 PR。
- 不得使用 `git add .`；必须按明确路径精确暂存文件。

## 开发顺序

- 先实现可独立测试的纯逻辑。
- 再使用 `unittest` 编写和运行测试。
- 最后接入 GUI。
- 技术栈继续使用 Python、PySide6 和 `unittest`。

## 架构约束

- 不得在单一 Widget 中堆积多个 Lab。
- 每个 Lab 应拥有独立的 controller、view model 和 widget。
- Lab 间共享能力应通过清晰、稳定的公共接口提供，避免跨 Lab 隐式耦合。

## 文件与发布约束

- 不得上传 `Cache*.pdf`。
- 不得上传环境目录或生成物，包括 `.venv`、`.wheelhouse`、`.codex-python`、`__pycache__`、`build`、`dist` 和 `outputs`。
- 不得复制 V1/V2 的 `.git`、环境目录、缓存、构建产物或其他被排除内容。

## 当前阶段

当前仅进行项目初始化、项目管理和文档规划，不进行业务功能开发，不复制 V2 源码，不安装依赖，不启动 GUI。
