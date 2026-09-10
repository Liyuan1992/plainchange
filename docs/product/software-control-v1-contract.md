# Software Control v1 数据合同

状态：PRD v2.0 语义合同已冻结，通用 HTML 投影已实现
适用范围：五问文本样本与确定性本地报告投影
Schema：`docs/product/schemas/software-control.v1.schema.json`

## 1. 目的

该合同把同一份已校验变化证据重新组织成软件负责人能理解和采取行动的五个答案。它不创建新的 Git、测试、用户行为、运行时或产品事实。

JSON 是系统合同，Markdown 是普通用户语义候选，HTML 是同一合同的确定性投影；三者必须表达相同答案和相同的信息优先级。生产渲染器只消费合同字段，不按项目名称、仓库路径或技术栈写分支。

## 2. 第一屏信息层级

第一屏不是五个等权问题的平铺。固定顺序为：

1. 一句话说明本次改动属于软件的哪个环节；
2. 直接说明目前看到的用户影响；
3. 直接说明仍需验证的风险边界；
4. 再进入五问解释；
5. “为什么这么判断”和技术证据继续下沉。

`first_screen_summary` 固定包含 `headline`、`internal_concept_label`、`confirmed_change`、`user_impact`、`residual_risk` 和 `owner_action`。`headline` 必须先说用户能理解的结果；内部术语只能放进次级的 `internal_concept_label`。四项结论分别保留自己的陈述状态和来源，不能因为被放在同一摘要里就合并成一个更强结论。

第一屏状态使用不超过八个汉字的短标签，例如“已确认”“目前没发现”“还没验证”。每项同时携带 `state_explanation`，页面点击状态后必须解释它的含义，尤其明确“目前没发现”不等于“已经证明不存在”。完整证据状态名保留在解释层，不作为正文句子反复出现。

默认首屏只展开十秒摘要；`five_questions` 置于“查看完整说明”之后，默认收起。收起只改变阅读层级，不能删除或改写五问内容和来源。

专业词检查不能只依赖禁词表。任何抽象名词都必须回答：“软件负责人不懂这个词，是否仍能作出下一步决定？”如果答案是否定的，就改成业务结果、具体例子或下沉到技术证据。

## 3. 固定五问

顺序和 ID 固定：

1. `software_operation`：这是个什么软件？
2. `current_change`：AI 这次主要改变了什么？
3. `affected_people`：谁可能感觉到变化？
4. `unknowns`：还有什么我们不知道？
5. `next_verification`：我接下来该检查什么？

缺少信息时保留问题并回答“不知道”，不得删除问题或用技术统计替代。

第 2 问遇到抽象规则变化时，`details.comparison_example` 必须用相同输入展示“以前”和“现在”的不同结果。第 3 问只回答谁可能感受到变化；第 4 问只列仍未完成的验证，不重复描述受影响对象。第 5 问用 `details.owner_checks` 给出负责人要确认的结果，具体样本构造和操作步骤保留在 `actions` 中供下钻。

## 4. 四种陈述状态

| 内部状态 | 页面含义 | 可以来自 | 不可以冒充 |
|---|---|---|---|
| `observed_fact` | 已有直接证据确认 | 已校验 Git、测试、绑定任务事实 | 完整运行时或用户影响 |
| `supported_interpretation` | 有依据，但经过解释步骤 | 多个已知事实、明确证据缺口 | 已观察事实 |
| `project_declared` | 项目自己定义的软件工作方式 | 带版本和 SHA 的项目配置或人工批准说明 | 静态代码自动发现或真实运行顺序 |
| `unknown` | 当前证据无法确认 | 缺少业务映射、运行时、用户或历史证据 | “确认没有影响” |

任何解释难度只能保持或降低状态，不能升级状态。

## 5. 来源绑定

每个回答都必须包含 `basis`：

- `claim_ids`：来自已校验 brief 的结论；
- `evidence_ids`：结论引用的证据；
- `component_ids`：来自项目声明软件地图的环节；
- `source_refs`：不能用上述 ID 表达的结构化来源位置。

ID 必须是源产物 ID 的子集。合同不允许为了让答案完整而发明一个看似真实的引用。

`source_identity.artifacts` 固定源文件的路径与 SHA-256。源文件变化后，旧样本必须重新生成或明确标记过期。

`control_identity` 的计算方式是：删除 `control_identity` 字段后，对剩余对象做 UTF-8、键排序、无多余空格的 canonical JSON，再计算 SHA-256 小写十六进制。

## 6. 软件工作地图

`working_map` 是项目声明层，不是静态 import 图或运行时追踪：

- 每个节点和关系的 `statement_state` 固定为 `project_declared`；
- `source.profile_id` 与 `profile_sha256` 必须能回到版本化目标配置；
- `change_state` 只有在变化证据可靠映射到该业务环节时才能写 `changed`；
- 一个实现分区映射到多个行为节点时，不能把整个分区变化自动分摊给所有节点，必须写 `unknown`；
- 技术实现通过 `implementation_group_ids` 下钻，不进入第一屏答案。
- `overview_map` 提供默认心智模型，节点必须覆盖全部详细节点且每个详细节点恰好出现一次；分组由来源合同声明，渲染器不得按项目名或节点名自行聚类。
- 若详细图存在 `changed` 节点，四步总览必须有且只有一个 `changed` 节点包含它。点击总览节点后，在同一画布切换到详细图并聚焦对应步骤。

“这个软件怎么工作”是独立第二屏，不是第一屏第 1 问的简单重复：

1. `screen_summary` 先用一句话说明输入、系统处理和人的决定权；
2. `nodes` 与 `flows` 组成一张从上到下的完整工作图；
3. 点击节点后，右侧读取该节点的 `owner_view`；
4. 技术实现最后才通过 `implementation_group_ids` 展开。

每个节点的 `owner_view` 必须回答：

- `meaning`：这一步在做什么；
- `visible_result`：负责人会看到什么结果；
- `current_change`：本次改动是否涉及这一步；
- `affected_people`：谁可能感受到变化；
- `unknowns`：关于这一步还有什么不知道；
- `owner_checks`：负责人需要确认什么；
- `basis`：上述表达的来源。

第一屏告诉负责人“这次改了什么”，第二屏把同一变化标回整个软件流程中的位置。`change_state=changed` 必须有直接对应的 claim/evidence/component 来源；不能因为多个流程节点共用一个实现分区，就把它们一起高亮。

## 7. 谁受到影响

`audience_impacts` 使用角色而不是文件：

- `very_likely`：有直接行为和变化证据；
- `possible`：存在有依据的路径，但还缺少运行验证；
- `not_observed`：在明确检查范围内暂未发现；
- `unknown`：没有可靠角色映射或证据范围不足。

`not_observed` 不能显示成“不会受到影响”。没有角色证据时，至少保留一个“软件使用者/负责人：目前无法判断”的显式条目。

## 8. 下一步行动

每条 `actions` 都是建议，不是执行结果：

- `basis_type=verified_change`：直接针对已确认变化；
- `basis_type=evidence_gap`：用于补齐一个明确未知项；
- `basis_type=project_checklist`：来自项目声明的验证清单。

`completion_status` 在本合同中固定为 `recommended_not_run`。只有真实测试回执进入证据主干后，另一个已观察事实才能说明测试结果；不能在建议对象上就地改成“已完成”。

`owner_checks` 与 `actions` 不是同一层：前者说明“负责人要确认什么结果”，后者才说明“测试人员如何构造条件并执行”。第一屏默认只显示 `owner_checks`。

## 9. 三层阅读

`evidence_layers` 固定为：

1. `software_control`：五问答案；
2. `explanation`：为什么这样判断、来源状态和未知边界；
3. `technical_evidence`：Diff、模块、静态关系和测试回执。

三层共享相同的 claim/evidence/component ID，不生成平行事实。

## 10. 降级规则

- 没有项目声明的软件地图：第一问回答缺少产品说明，并保留技术证据入口。
- 只有代码变化、没有行为映射：第三问必须是 `unknown`。
- 只有 AI 回复、没有用户确认：原因只能显示为对话线索。
- 没有实际测试回执：不能声称测试通过。
- 有测试回执但没有运行时覆盖说明：不能扩展为“用户行为没有变化”。
- 静态关联存在：最多支持代码层面的影响范围，不能自动生成用户角色影响。

## 11. 当前验证边界

Change Passport 自身样本是已知上下文的正确性样本，用于暴露合同问题。它不是盲测，也不证明自动生成器已经能为任意项目写出同等质量的普通语言。

自动 Schema、ID、哈希和文本一致性检查不等于人类理解测试。`human_comprehension_status` 在独立参与者完成五问前必须保持 `pending_independent_participant`。
