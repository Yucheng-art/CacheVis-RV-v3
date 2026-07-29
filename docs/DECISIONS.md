# 决策记录

## D-001：V3 使用独立仓库

- 状态：已决定
- 决策：V3 不继承 V1/V2 的 Git 历史，使用独立仓库管理。
- 原因：隔离归档版、稳定版与多 Lab 平台版的生命周期。

## D-002：V1/V2 只读

- 状态：已决定
- 决策：V1 与 V2 仅供参考，不修改文件、不提交、不改变 Git 状态。
- 原因：保护归档成果和稳定版本。

## D-003：按纯逻辑、测试、GUI 的顺序开发

- 状态：已决定
- 决策：先实现纯逻辑，再使用 `unittest` 验证，最后接入 PySide6 GUI。
- 原因：降低界面耦合并提高规则的可验证性。

## D-004：每个 Lab 独立分层

- 状态：已决定
- 决策：每个 Lab 拥有独立 controller、view model 和 widget，不在单一 Widget 中堆积多个 Lab。
- 原因：支持清晰边界、独立测试与持续演进。

## D-005：初始化阶段不开发业务功能

- 状态：已决定
- 决策：仓库初始化阶段仅建立项目管理、文档骨架和 Git/GitHub 仓库。
- 原因：先固定边界和协作约束，避免把规划误写为实现。

## D-006：平台采用 Sidebar、Home、Registry 与页面栈

- 状态：已决定
- 决策：V3 平台使用 Sidebar 导航、Home 元数据入口、集中式 Lab Registry 和 `QStackedWidget` 页面栈。
- 原因：将平台协调职责与各 Lab 业务实现隔离，并为多 Lab 扩展提供稳定入口。

## D-007：可用 Lab 惰性创建并缓存

- 状态：已决定
- 决策：可用 Lab 仅在首次导航时由 Registry factory 创建，随后缓存并复用；Coming Soon Lab 不提供 factory。
- 原因：减少启动时耦合和开销，同时确保页面切换不丢失状态，避免误用尚未实现的 Lab。

## D-008：M0 保持 V2 行为兼容

- 状态：已决定
- 决策：M0 的 package 提取与平台化不改变 Cache 算法、替换策略和已有实验行为，扁平路径在迁移期继续由兼容 facade 支持。
- 原因：以稳定、可回归的 V2 行为作为 V3 后续教学 Lab 的基础。

## D-009：Miss Type Lab 从严格 3C 纯逻辑开始

- 状态：已决定
- 决策：M1 首先实现不依赖 PySide6 的 3C Miss 分类核心和测试，在 GUI 完成前 Registry 中继续保持 Coming Soon。
- 原因：先固定教学定义与分类不变量，再设计展示和交互。

## D-010：基础 3C 分类使用 memory block 与 fully associative LRU reference

- 状态：已决定
- 决策：Miss Type Lab 以 memory block 为 seen-before 和分类单位；Reference Cache 与 Actual Cache 容量、block size 相同，采用 fully associative、单 set、LRU 配置。Actual Cache 在该 Lab 中固定使用 LRU。
- 原因：排除 block offset 和替换策略差异的干扰，使 compulsory、conflict、capacity 的分类符合严格基础 3C 定义。

## D-011：历史 Timeline 选择不回滚 Cache 与累计统计

- 状态：已决定
- 决策：选择历史 Timeline step 只更新 Selected Evidence；Current Access、Actual Cache、Reference Cache 与累计 Statistics 保持最新执行状态。
- 原因：当前实现不保存每一步的完整 Cache snapshot，明确区分“查看历史证据”和“回滚模拟状态”，避免界面暗示尚未实现的历史回放能力。

## D-012：Miss Type Lab 通过 Registry 成为可用 Lab

- 状态：已决定
- 决策：M1.3 完成后，Miss Type Lab 状态改为 Available，由 Registry factory 延迟创建并由 Main Window 缓存；Home 与 Sidebar 继续完全由 Registry 元数据驱动。
- 原因：复用既有平台扩展机制，不在 Main Window 中加入 Miss Type 专用分支，并确保页面切换后实验状态保持。

## D-013：Locality 使用互斥的教学主证据分类

- 状态：已决定
- 决策：exact address 已访问分类为 `TEMPORAL`；address 未访问但 block 已访问分类为 `SPATIAL`；block 未访问分类为 `FIRST_TOUCH`。
- 原因：现实访问可能同时体现多种局部性特征，但互斥主证据有利于逐步展示判断链路、建立稳定统计不变量，并避免含糊的 unknown 状态。

## D-014：Locality 证据与 Cache HIT/MISS 相互独立

- 状态：已决定
- 决策：F/S/T 只由访问历史确定，不由 Cache 结果反推；HIT 不自动代表 Temporal，MISS 不代表没有 locality。历史 Timeline 选择只更新 Selected Evidence，不回滚 Current Access、Cache、Statistics 或 Block Map。
- 原因：局部性描述访问模式，Cache 结果还取决于容量、映射、替换策略和访问顺序；分离两者可避免错误教学结论。

## D-015：Block reuse distance 使用 distinct-block recency stack

- 状态：已决定
- 决策：维护 MRU→LRU 的 distinct-block recency stack，访问前目标 block 所在索引作为 block reuse distance；首次访问没有 reuse distance。
- 原因：该定义确定、可测试，并能直观表达两次访问同一 block 之间出现了多少不同 block。

## D-016：Locality Lab 通过 Registry 成为可用 Lab

- 状态：已决定
- 决策：M2.3 完成后 Locality Lab 状态改为 Available，由 Registry factory 延迟创建并由 Main Window 缓存；Home 与 Sidebar 继续由 Registry 元数据驱动。
- 原因：保持平台扩展机制一致，避免在 Main Window 中增加 Locality 专用业务分支，并确保页面切换后实验状态保持。

## D-017：Policy Lab 同步比较三种正式 replacement policy

- 状态：已决定
- 决策：Policy Lab 对同一 Cache size、block size、ways、address width 和 address trace 同步运行 `LRU`、`FIFO`、`Random` 三条独立 lane，唯一变化为 core 接受的 replacement policy 字符串。
- 原因：控制其他变量，直接展示替换策略如何改变 victim、Cache state 与后续 HIT/MISS；项目没有正式 `ReplacementPolicy` enum，因此不创建重复枚举。

## D-018：Policy 决策严格区分 HIT、INVALID_FILL 与 EVICTION

- 状态：已决定
- 决策：目标 tag 已存在时为 `HIT`；目标 tag 不存在但有 invalid way 时为 `INVALID_FILL`；只有目标 tag 不存在且映射 set 已满时才为 `EVICTION`。Invalid fill 不驱逐有效 line，也不属于 replacement。
- 原因：避免把所有 miss 都错误描述为 replacement，并明确 replacement policy 只有在 full-set miss 时才参与 victim 选择。

## D-019：Random lane 使用隔离的 seeded replay

- 状态：已决定
- 决策：Session 持有独立 `random.Random(seed)` 状态；每次 Random access 临时切换模块级 random 状态，正式调用一次 `CacheSimulator`，保存私有随机状态，并在 `finally` 中恢复进程全局状态。不得修改 core、复制 Random victim 算法或留下未恢复的全局 seed。
- 原因：在复用 core 正式 Random 行为的同时获得可复现性，并隔离不同 Session 与进程其他代码的随机状态。

## D-020：Policy 历史选择只切换决策证据

- 状态：已决定
- 决策：选择历史 Timeline step 只更新 `selected_step`、Selected Decision Evidence 和 Timeline SELECTED；Current Access、LRU/FIFO/Random Cache state、Statistics、Divergence Summary、Random stream 与 `next_step_index` 保持最新执行状态。
- 原因：明确区分历史证据查看与模拟状态回滚，避免消费额外随机数或暗示尚未实现的历史 Cache snapshot 能力。

## D-021：Policy Lab 通过 Registry 成为可用 Lab

- 状态：已决定
- 决策：M3.3 完成后 Policy Lab 状态改为 Available，由 Registry factory 延迟创建并由 Main Window 通用 page cache 复用；Home 与 Sidebar 继续由 Registry 元数据驱动。
- 原因：保持平台扩展机制一致，不在 Main Window 中加入 Policy 专用分支，并确保页面切换后实验状态保持。

## D-022：Performance 使用显式教学时序而非 wall-clock

- 状态：已决定
- 决策：Performance Lab 的 cycle、AMAT 和 speedup 全部由用户可见的 hit time、fixed miss overhead 与 transfer cycles/byte 计算；不得使用宿主机 Python wall-clock benchmark 代表 Cache 性能。
- 原因：wall-clock 会混入解释器、操作系统与机器差异，不能稳定表达硬件教学模型。

## D-023：Performance sweep 每个 point 从冷 Cache 独立运行

- 状态：已决定
- 决策：每个 sweep point 使用正式 `PerformanceRunner` 从空 Cache 开始；支持 LRU/FIFO，Random 明确拒绝并归入 Policy Lab。选择 point 或 chart metric 只重建 view state，不重新运行 sweep。
- 原因：避免前一个 point 污染后一个 point，并保证比较、tie 和 selection 语义稳定可测试。

## D-024：单级 sweep 与 analytical L1/L2 相互独立

- 状态：已决定
- 决策：Run/Clear Sweep 不清除 hierarchy；Analyze/Clear Hierarchy 不清除 sweep。L1/L2 当前只计算概率和 expected-cycle contributions，不创建第二级 CacheSimulator。
- 原因：明确区分基于实际单级 Cache trace 的 sweep 与尚无实际 L2 contents 的 analytical timing model。

## D-025：Performance Lab 通过 Registry 成为可用 Lab

- 状态：已决定
- 决策：M4.3 完成后 Performance Lab 状态改为 Available，由 Registry factory 延迟创建并由 Main Window 通用 page cache 复用；Write Policy 继续为 Coming Soon 且 `factory=None`。
- 原因：保持平台扩展与状态缓存机制一致，不向 Main Window 添加 Performance 专用分支。

## D-026：Core 拥有 write-policy 语义

- 状态：已决定
- 决策：write-through/write-back、write-allocate/no-write-allocate、dirty marking、bypass 与 dirty eviction 均由正式 `CacheSimulator` 决定。
- 原因：避免 Lab、GUI 或教学解释层复制并分叉 Cache 行为。

## D-027：Explainer 只解释正式 AccessResult

- 状态：已决定
- 决策：Write Policy Explainer 只消费正式 `AccessResult`，不重算 hit、allocation、bypass、victim 或 dirty transition。
- 原因：让教学证据与实际模拟结果保持同一事实来源。

## D-028：实际 eviction 以 evicted_way 为准

- 状态：已决定
- 决策：M5 使用 `evicted_way` 表示实际被覆盖的 way；`victim_way` 只保留旧调用兼容用途，不作为 Lab eviction 证据。
- 原因：区分候选 victim 与确实发生的 eviction，并避免 invalid fill 或 bypass 被误报为替换。

## D-029：Runtime traffic 与 final dirty drain 分开

- 状态：已决定
- 决策：运行期间 block fill、immediate store、bypass、dirty write-back 与运行结束时 resident dirty data 的分析值分别报告。
- 原因：避免把尚未写回的数据误计入 runtime，也避免在 workload 结束比较中忽略 Write-Back 留存的脏数据。

## D-030：Final drain 是非变异分析值

- 状态：已决定
- 决策：final drain 不修改 Cache、不调用 flush，也不构成 trace step；它仅由运行结束时 valid 且 dirty 的 resident line 计算。
- 原因：保持 Timeline、step count、Cache state 与正式 trace 语义不变。

## D-031：四 lane 使用独立 CacheSimulator

- 状态：已决定
- 决策：WT+WA、WT+NWA、WB+WA、WB+NWA 各自拥有独立 simulator，同步消费相同 trace，不从一条 lane 复制另一条结果。
- 原因：每种策略组合必须保有独立 Cache、replacement metadata 与 dirty state，才能观察后续 outcome divergence。

## D-032：No-Write-Allocate bypass 不触发 victim selection

- 状态：已决定
- 决策：NWA write miss 是 MISS，但不分配、不选择 victim，也不改变 resident Cache state 或 replacement metadata；store 直接 bypass 到 lower memory。
- 原因：这是 no-write-allocate 的正式语义，也是 allocation 与 future reuse 对比的基础。

## D-033：历史选择不回滚当前运行状态

- 状态：已决定
- 决策：选择历史 Timeline step 只切换 access、decision、traffic delta 与 divergence evidence；current Cache、statistics、final dirty state 和运行位置保持最新。
- 原因：当前实现保存历史证据而非每一步完整可恢复 session，明确区分审阅与回滚可避免误导。

## D-034：Dirty-state divergence 与 full cache-state divergence 分开

- 状态：已决定
- 决策：dirty-state 仅比较每个位置的 valid/dirty；full cache-state 比较 valid、tag、dirty、last_used 与 insert_time 的完整 snapshot。
- 原因：传播策略可以先改变脏位而不改变 tag，完整状态也可能因 metadata 不同而分叉，两种现象具有不同教学含义。

## D-035：Write Policy GUI 不包含 Random replacement

- 状态：已决定
- 决策：Write Policy Lab 固定使用确定性的 replacement 配置，不在四 lane GUI 中加入 Random。
- 原因：避免 replacement randomness 与 write-policy 差异混杂；Random 的教学比较由 Policy Lab 负责。

## D-036：当前 trace 的最低流量不代表普遍最优

- 状态：已决定
- 决策：所有 leader 支持 tie，并固定提示结果仅适用于当前 trace、Cache 配置与 traffic assumptions，不宣称任一策略普遍最优。
- 原因：流量、hit rate 与 final dirty data 均依赖 workload 和模型假设，有限 trace 不能建立普适排序。
