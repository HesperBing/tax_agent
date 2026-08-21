# Schema v1.1 冻结说明

## 1. 依据与优先级

本版结构依据：

1. `agent统一原则_v0.6.md`
2. `01_Tax_Judgement_业务规则_v2.1.md`
3. `02_风险分类_v2.1.md`
4. `03_评分维度_v2.1.md`
5. `04_Evidence_Coverage_维度_v2.1.md`
6. `agenthandoff_v0.1` 中的法规、Temporal RAG、Mock 与 Golden Cases

发生冲突时，采用统一原则 v0.6 的定义。

## 2. 版本定义

- 项目接口版本：`v1.1`
- JSON Schema 官方方言：Draft 2020-12
- 只有最终 Root `agent_schema.json` 保存 `schema_version`
- 子模块通过 Git 文件版本和 `$id` 管理，不在运行结果中重复保存 `schema_version`

## 3. 已冻结的结构决策

- 全项目字段使用 `snake_case`。
- 所有顶层模块均携带 `tax_case_id`。
- Root 必须保留 `rule_engine_input`，用于审计本次实际输入。
- 业务日期使用 `YYYY-MM-DD`；未知日期使用 `null`。
- 正式事件型 `actual_*` 对象不保存通用 `status`。
- Actual Fact 不存在不表示 `confirmed_not_done`。
- Evidence State 只允许 `provided / missing / unknown / not_applicable`。
- `provided` 必须至少引用一个 `supporting_source_file_id`。
- Consistency Check 只比较 Contract Facts 与 Actual Facts。
- Rule Engine Output 固定为 `rule_execution_results[]` 和 `judgement_resolution_results[]`。
- Tax Judgement 只从 Judgement Resolution 形成。
- Formal Risk Event 只从固定 Risk Trigger Rule 形成。
- Next Actions 只能引用正式 Risk Event。
- Tax Health Score 与 Evidence Coverage 分开计算。
- 模块结构默认 `additionalProperties: false`，新增字段必须升级Schema并走Change Log。

## 4. 旧v0.1接口迁移决定

| 旧字段/结构 | v1.1处理 |
|---|---|
| `case_id` | 统一改为 `tax_case_id` |
| 每个Mock中的`schema_version` | 删除，仅Root保留 |
| `component_id` | 按语义改为`substance_component_id`或`transaction_fact_id` |
| Consistency输入包含Evidence、Tax Judgement | 删除，只引用Contract/Actual Facts |
| Consistency输出的`legal_value`、`regulation_refs`、`candidate_risk_codes` | 删除，法律判断进入Regulation/Rule Engine链路 |
| `needs_information`分支 | 不作为正式业务事实状态；无法检索时返回技术错误或业务`unknown/needs_review` |
| Actual Fact中的`pending/unknown`事件状态 | 删除；事件存在表示已观察到，未发生阶段由其他业务结果表达 |
| 法规节点`source_url` | v1.1运行结果统一为`source`，导入CSV时做字段映射 |
| 未分类文件以`unknown`进入`source_files[]` | 禁止；进入`file_processing_errors[]` |

## 5. 规则冲突处理

### Overpayment

专项规则列出了`vat_overpayment`、`cit_overpayment`和`tax_overpayment`评分Profile，但统一原则v0.6规定多缴税原则上不形成Formal Tax Health Risk。因此v1.1将多缴保留在Tax Impact和Final Report，不进入正式Risk Event评分。

### Stamp Tax

交接包包含印花税筛查，但统一原则v0.6没有预定义`stamp_tax`顶层Tax Judgement模块。因此v1.1允许Regulation Result通过Tax Type Registry表达印花税事项，但不新增Tax Judgement顶层模块。

### Corporate Income Tax

交接包首版范围将企业所得税列为范围外，但统一原则v0.6和Tax Judgement v2.1均定义了`corporate_income_tax`模块。v1.1保留该模块；实际启用仍由Scope和Tax Type Registry控制。

## 6. Registry边界

以下值不在Schema中写死全部枚举，而是校验为`lower_snake_case`并要求运行时存在于最新版Registry：

- Tax Type
- Economic Substance
- Invoice Type
- Scope Type
- Contract Fact Relation Type
- Risk Event Type
- Rule Domain
- Judgement Item

Schema负责结构和类型，Registry负责跨模块业务代码的合法集合。正式联调前必须冻结相应Registry。

## 7. JSON Schema之外的确定性校验

JSON Schema标准本身不能直接比较两个远端字段是否相等，因此以下规则由`tests/test_schema_validation.py`补充：

- 所有顶层模块`tax_case_id`一致；
- `case_status`由`module_statuses`确定性派生；
- 五维权重、Risk Level和Health Score公式正确；
- Evidence Coverage扣分公式正确；
- Next Actions只引用正式Risk Event。

## 8. 接口冻结前仍需业务成员确认

结构Schema已经可用于开发和联调，但下列Registry内容仍需团队冻结：

- Economic Substance Registry
- Tax Type Registry
- Invoice Type Registry
- Evidence Requirement Registry
- Tax Treatment Item Registry
- Risk Event Registry
- Contract/Actual Fact Relation Type Registry
- Scope Type Registry
- Risk Trigger Rule Registry
- Scoring Profile与Mapping Tables

这些Registry更新不应直接改动已冻结字段结构；如果必须增加字段，则升级Schema版本并更新Mock、Golden Test和CHANGELOG。
