# Tax Agent 统一原则 v0.6

> 本版本在 `v0.5` 基础上，正式扩充 Actual Facts 的实际税务处理能力，并同步 `actual_tax_treatments[]`、`actual_obligation_states[]`、`tax_filing_material`、Tax Treatment Item Registry、Actual Fact Relation Type Registry、Risk Trigger 固定模式、Risk Event Registry 与 Tax Health Score Mapping。  
> 本文件是三人协作、Schema、Prompt、Temporal RAG、Rule Engine、Dify Workflow、测试与最终报告共同遵守的最高项目规范。  
> 如果其他业务文档、旧版规则、Prompt、代码或 Dify 节点与本文件冲突，以本文件及其引用的最新正式业务规则为准。

---

# 一、适用范围与产品边界

当前 Agent 聚焦：

```text
中国合同收入税务健康评分
```

当前业务范围：

```text
合同收入方向
自然人
境内企业
服务类及相关合同交易
```

当前版本不设置用户自然语言事实补充入口。

一个 `Tax Case` 只对应一个核心合同关系：

```text
主合同
+ 补充协议 / 变更协议
+ 与该合同关系对应的实际履约、开票、付款、税务材料
```

彼此独立的合同必须建立不同 Tax Case。

系统事实来源仅来自同一 Tax Case 中已经完成文件分类并进入正式 `source_files[]` 的材料。文件分类失败的材料不得进入正式事实来源集合，但单个非关键文件分类失败不阻断整个 Case。

当前总体严格单向链路统一为：

```text
用户创建 Tax Case
↓
上传文件
↓
文件分类与合同文件角色识别
↓
Contract Facts
+ Contract Fact Relations
↓
Economic Substance（仅基于 Contract Facts）
+
Actual Facts
+ Actual Tax Treatments
+ Actual Obligation States
+ Actual Fact Relations（Actual ↔ Contract）
+
Evidence Requirement / Instance / State
↓
Transaction Facts（引用组合视图）
↓
Consistency Check（仅 Contract Facts ↔ Actual Facts）
↓
Temporal RAG
↓
Regulation Result
↓
Rule Engine Input
↓
Atomic Rule Execution
↓
Judgement Resolution Results
↓
Tax Judgement
↓
Tax Impact Result
↓
Risk Trigger Rules
（对比 Judgement Resolution / Tax Impact / Actual Tax Treatment / Actual Obligation State 等）
↓
Risk Events
↓
Tax Health Score
+
Evidence Coverage
↓
Next Actions
↓
Final Report
↓
agent_schema.json（完整 Case 最终快照）
```

禁止形成：

```text
Tax Judgement → Rule Engine → Tax Judgement
```

等循环依赖。

# 二、必须统一的数据对象

以下数据对象必须使用统一名称、统一结构、统一字段定义：

1. `Tax Case`
2. `Contract Facts`
3. `Contract Fact Relation`
4. `Actual Facts`
5. `Actual Tax Treatment`
6. `Actual Obligation State`
7. `Actual Fact Relation`
8. `Actual Fact Issue / Duplicate Group`
9. `Economic Substance`
10. `Evidence Requirement`
11. `Evidence Requirement Instance`
12. `Evidence State`
13. `Transaction Facts`
14. `Consistency Check Result`
15. `Regulation Result`
16. `Rule Engine Input`
17. `Rule Engine Output`
18. `Tax Judgement`
19. `Tax Impact Result`
20. `Risk Trigger Rule`
21. `Risk Event`
22. `Tax Health Score`
23. `Evidence Coverage`
24. `Next Actions`
25. `Final Report`

同时统一维护以下配置对象：

```text
Economic Substance Registry
Tax Type Registry
Invoice Type Registry
Evidence Requirement Registry
Risk Event Registry
Tax Treatment Item Registry
Contract Fact Relation Type Registry
Actual Fact Relation Type Registry
Scope Type Registry
Rule Registry
Risk Trigger Rule Registry
Scoring Profile Registry
Scoring Rules / Mapping Tables
Working Day Calendar Registry
Shared Enums / Registries
```

任何模块需要新增或修改：

```text
字段
枚举
JSON 结构
Registry 项
Rule 状态
评分规则
跨模块引用语义
```

必须先更新统一定义，再修改 Prompt、Schema、Rule Engine、Dify 或代码。

# 三、统一字段命名规则

全项目统一使用：

```text
snake_case
```

例如：

```text
contract_date
income_type
evidence_coverage
transaction_stage
risk_event_id
health_score_loss
```

同一含义禁止出现多套命名。

正式字段名一旦冻结，不得随意改名。

---

# 四、统一字段类型

每个字段必须明确类型。

允许的主要类型：

```text
string
number
boolean
date
datetime
enum
array
object
null
```

同一字段在不同模块中必须保持同一类型。

---

# 五、统一日期格式

所有业务日期统一：

```text
YYYY-MM-DD
```

日期无法确认：

```text
null
```

禁止使用：

```text
""
"unknown"
"不确定"
"暂无"
```

代替空日期。

---

# 六、统一时间字段含义

以下时间概念必须严格区分：

```text
contract_date
transaction_date
payment_date
performance_date
delivery_date
acceptance_date
vat_tax_liability_time
corporate_income_recognition_time
individual_income_tax_time
withholding_time
invoice_time
regulation_valid_from
regulation_valid_to
```

不得将不同时间概念统一压缩为一个通用 `date` 字段。

---

# 七、统一金额与币种格式

金额统一使用：

```text
number
```

币种单独使用：

```text
currency
```

禁止将金额与币种拼成自由文本。

对于部分已确认金额，可使用：

```json
{
  "known_amount": 60000,
  "total_amount": null,
  "currency": "CNY"
}
```

已确认下限可用于后续阈值规则判断，但不得把未知总额伪造为确定金额。

---

# 八、统一枚举值

## 8.1 事实状态

项目仍保留以下通用事实状态枚举，供确有状态型事实对象时使用：

```text
confirmed_done
confirmed_not_done
unknown
pending
not_applicable
```

但当前正式 `actual_*` 事件对象**不保存 `status`**：

```text
Actual Fact 对象存在
= 当前材料已经观察到该实际事件

Actual Fact 对象不存在
≠ 自动等于 confirmed_not_done
```

## 8.2 证据状态

统一使用：

```text
provided
missing
unknown
not_applicable
```

## 8.3 一致性状态

统一使用：

```text
consistent
partial
inconsistent
unknown
needs_review
```

## 8.4 Rule 结果状态

统一使用：

```text
confirmed_triggered
confirmed_not_triggered
provisional_triggered
provisional_not_triggered
unknown
```

## 8.5 Tax Judgement 状态

统一使用：

```text
confirmed
partial
unknown
not_applicable
```

适用于：

```text
整体 judgement_status
模块 status
原子判断项 status
```

## 8.6 风险等级

统一使用：

```text
low
medium
high
critical
```

## 8.7 Case 状态

`case_status` 统一使用：

```text
created
processing
failed
completed
```

各模块统一技术运行状态：

```text
not_started
running
completed
failed
```

`case_status` 不允许独立人工维护，必须由 `module_statuses` 确定性计算：

```text
全部 not_started
→ created

存在 running，或部分模块已完成、其余尚未开始
→ processing

任一当前必须执行的核心模块 failed
→ failed

本 Case 所需全部核心模块 completed
→ completed
```

业务上的：

```text
unknown
partial
needs_review
conflict
Evidence missing
```

不等于技术执行失败。只要 Workflow 正常完成，仍可 `case_status = completed` 并生成 Final Report。

# 九、统一 unknown 处理规则

`unknown` 表示：

> 当前已有事实、法规或证据不足，暂时无法形成可靠确定结论。

必须遵守：

- `unknown` 不直接视为违规；
- `unknown` 不直接视为已完成；
- `unknown` 不直接视为未完成；
- 缺少材料优先影响 Evidence Coverage；
- 只有事实和证据足够时，Rule Engine 才能确认事项完成或未完成；
- LLM 推断、系统猜测、RAG 内容、Rule Engine 输出、Final Report 均不得把 `unknown` 强行改写为确定事实；
- 当前版本不通过用户自由描述或补充问答填补 `unknown`。

---

# 十、统一 pending 处理规则

`pending` 表示：

> 按当前交易阶段，该事项尚未进入应发生阶段。

必须区分：

```text
pending
= 事情尚未到发生阶段

unknown
= 事情可能已经发生，但当前无法确认
```

当前正式 `actual_*` 事件对象不使用 `pending` 状态。

对于 Evidence Requirement Instance：

```text
尚未到 check_due_date
→ Instance 可以提前存在
→ 暂不生成 Evidence State
→ 不进入 Evidence Coverage 评分
```

不得使用：

```text
not_applicable
```

代替“尚未到应检查时点”。

`not_applicable` 只表示该证据要求在业务上真正不适用。

---

# 十一、统一事实层级

## 11.1 Contract Facts

表示：

```text
合同写了什么
```

事实来源仅限当前 Tax Case 中合同文件及其提取结果。

Contract Facts 只保存合同约定及合同明确可确认的结构化内容，不接收 Actual Facts、Tax Judgement、RAG 或 Rule Engine 的反向回填。

## 11.2 Actual Facts

表示：

```text
材料直接证明实际发生了什么
```

事实来源仅限当前 Tax Case 中实际交易、履约、申报、缴税及其他税务执行材料。

当前正式 Actual Facts 采用事件数组；一般事件对象存在即表示事件已被观察到，因此不再保存统一 `status`。

一般 Actual Fact 应能够对应至少一个 Contract Fact。

明确例外：

```text
actual_tax_filings[]
actual_tax_payments[]
actual_tax_treatments[]
actual_obligation_states[]
```

属于法定义务或实际税务处理事实，即使合同没有 `tax_compliance_terms[]`，也允许以：

```text
Tax Case
+ tax_type
+ tax_period
```

层级独立存在。

`actual_tax_treatments[]` 用于保存企业在正式申报或其他税务执行材料中实际采用的税务处理。一个对象只表达一个原子 `treatment_item`，不得把一整张申报表压成一个不可比较的大对象。

`actual_obligation_states[]` 仅保存材料能够正面确认的义务履行状态：

```text
confirmed_done
confirmed_not_done
```

不得因为未找到材料、Evidence missing 或数组为空而推定 `confirmed_not_done`。

## 11.3 Evidence State

表示：

```text
当前上传材料对具体 Evidence Requirement Instance 的支持状态
```

Evidence State 只针对 Actual Facts / 实际执行证据要求，不对 Contract Facts 单独建立 Evidence State。

Contract Facts 通过其 `sources[]` 追溯合同来源。

三类信息必须分层保存，不得混用。

---

# 十二、统一事实来源边界

当前正式 `source_file_type` 包括：

```text
contract
invoice
payment_receipt
withholding_certificate
tax_filing_material
tax_payment_certificate
acceptance_material
delivery_material
other
```

合同类文件进一步记录：

```text
main_contract
supplementary_agreement
amendment_agreement
```

文件分类无法可靠完成时：

```text
→ 不进入正式 source_files[]
→ 不得支持 Contract Facts / Actual Facts / Evidence State
→ 作为文件处理技术错误单独记录
```

单个文件分类失败原则上不阻断整个 Tax Case；只有当有效输入已经不足以完成必要核心模块时，对应模块才允许失败。

以下内容不得作为 Contract Facts、Actual Facts、Evidence State 的事实来源：

```text
LLM 推测
LLM 假设
Final Report
Temporal RAG 法规内容
Regulation Result
Rule Engine 输出
评分结果
整改建议
```

LLM 只能理解和结构化已进入正式 source_files[] 的材料，不得创造材料中不存在的实际事实。

# 十三、统一 Evidence State 判断逻辑

Evidence State 以：

```text
Evidence Requirement Instance
```

为最小判断对象，不以整个 Tax Case 中是否出现过同类文件为单位。

## provided

表示当前 Tax Case 已存在能够支持该具体 Requirement Instance 的有效材料。

至少满足：

- 可归属于当前 Tax Case；
- 内容可识别；
- 与该 Requirement Instance 直接相关；
- 能够为目标 Actual Fact / 业务事项提供有效支持。

文件已经上传，不自动等于 `provided`。

## missing

表示：

```text
该 Evidence Requirement Instance 已到应检查时点
+
当前 Tax Case 没有有效支持材料
```

必须遵守：

```text
evidence_state = missing
≠
Actual Fact 已确认未发生
```

即使没有对应 Actual Fact，Evidence State 仍可通过 `evidence_requirement_instance_id` 表达该具体证据要求已经缺失。

## unknown

适用于：

- 文件归属无法确认；
- 文件内容无法可靠识别；
- 材料与具体 Requirement Instance 对应关系无法确认；
- 多份材料之间存在冲突；
- 当前条件不足，无法判断材料是否满足该要求。

不得自动转成 `provided` 或 `missing`。

## not_applicable

仅表示：

- 该证据要求对当前具体业务实例真正不适用。

尚未到检查时点不得使用 `not_applicable`。

Evidence State 只保存最小 Evidence Requirement 的状态；Evidence Requirement Group 的结果由规则计算，不重复保存 Group Evidence State。

---

# 十四、多材料冲突处理

同一业务事实存在冲突材料时：

1. 各材料分别保留来源；
2. 不得为了得到确定结论而任意选择一份材料；
3. 已能确认“事件发生”但部分字段无法确认时，允许生成 Actual Fact，无法确认字段使用 `null`；
4. 若事件本身都无法确认，则不强行生成 Actual Fact；
5. 差异交由 Consistency Check 或 Evidence State 输出；
6. 冲突可影响 Evidence Coverage；
7. 冲突本身不直接等于税务违规；
8. LLM 不允许自行消除冲突。

---

# 十五、统一 Transaction Facts

`Transaction Facts` 是事实层向规则层提供的引用组合视图，不复制上游事实值。

核心结构：

```text
transaction_fact_id
economic_substance_ref
substance_code
contract_fact_refs[]
actual_fact_refs[]
evidence_state_refs[]
```

三类引用必须分开保存，不合并为通用 `object_refs[]`。

即使：

```text
classification_status = uncertain
substance_code = null
```

也允许生成 Transaction Fact，并通过 `economic_substance_ref` 保持与具体 Economic Substance Component 的稳定关系。

当引用存在父子结构的 stage 时：

```text
引用 stage
+
同时引用其父 term
```

以保证后续 Rule Engine 能取得父级默认属性与子级覆盖信息。

默认：

```text
一个 Economic Substance Component
→ 一个 Transaction Fact
```

只有结构化 Contract Fact 关系图与 Actual↔Contract 对应关系能够证明存在彼此独立交易链时，才允许同一 Component 拆成多个 Transaction Fact。

以下因素单独存在时不足以拆分：

```text
阶段不同
付款次数不同
金额不同
日期不同
发票分批开具
```

`actual_tax_filings[]` 与 `actual_tax_payments[]` 保持 Tax Case + tax_type + period 级事实，不强制加入 Transaction Fact。

# 十六、统一文件来源记录

每条关键 Contract / Actual Fact 对象及 stage 应尽量记录：

```text
sources[]
```

每个 source 至少可包含：

```text
source_file_id
source_page
source_text
extraction_confidence
```

`source_file_type`、文件名、合同文件角色等文件级信息统一通过 `source_file_id` 回到 Tax Case 的 `source_files[]` 查询，不在每个 Fact source 中重复保存。

`term` 与 `stage` 均可有自己的 `sources[]`：

```text
term.sources[]
→ 证明整套安排

stage.sources[]
→ 证明该具体阶段
```

同一事实存在多个来源时允许保留多份 source。

# 十七、统一置信度范围

所有模型提取置信度统一：

```text
0.00 - 1.00
```

`extraction_confidence` 只用于提取质量监控，不设置统一硬阈值决定 Fact 是否成立。

禁止：

```text
confidence < 0.8
→ 一律不能进入 Facts
```

正式 Fact 是否成立仍根据：

```text
原始材料是否明确
是否能够可靠识别
是否存在冲突
是否能够确认与当前 Tax Case 的对应关系
```

高置信度不能覆盖材料冲突；低置信度也不自动等于事实无效。

# 十八、统一 Economic Substance 原则

Economic Substance 只基于：

```text
Contract Facts
```

进行分类。

不得使用：

```text
Actual Facts
Evidence State
Tax Judgement
Rule Engine Output
```

反向改变 Economic Substance。

统一对象：

```text
economic_substance_components[]
```

每个 component 至少包含：

```text
substance_component_id
substance_code
classification_status
role
amount
currency
contract_fact_refs[]
```

Economic Substance 不重复保存 `sources[]`。分类依据追溯统一为：

```text
Economic Substance
→ contract_fact_refs[]
→ Contract Fact.sources[]
→ 原始合同
```

规则：

```text
一个 component
→ 最多一个 substance_code

无法可靠分类
→ classification_status = uncertain
→ substance_code = null
```

同一 `substance_code`：

```text
属于同一业务链
→ 合并

属于结构化关系能够确认的彼此独立交易链
→ 允许存在多个 component
```

`classification_status`：

```text
classified
uncertain
```

`role`：

```text
primary
ancillary
independent
null
```

# 十九、统一 Mixed Economic Substance

Mixed Economic Substance 在以下情况下成立：

```text
存在 >= 2 个不同的已分类 substance_code
```

或：

```text
至少一个已分类 component
+
至少一个 classification_status = uncertain 的独立实质 component
```

同一 `substance_code` 的多个独立 Component 本身不构成 Mixed；是否 Mixed 看不同 `substance_code` 或独立未分类实质。

Tax Judgement 仍按 `substance_code` 聚合。同一原子项同一 `substance_code` 最多一个 detail。

同一 `substance_code` 下不同独立交易如果依法存在不同处理，使用既有：

```text
treatments[]
+
treatment_scope
```

区分具体适用范围，不新增 Tax Judgement 主层级。

# 二十、统一 Economic Substance 金额规则

Economic Substance component 的：

```text
amount
currency
```

只允许保存**合同直接、明确归属于该 substance 的金额**。

例如：

```text
软件开发费 800000
维护费 200000
```

可以分别进入对应 component。

以下金额不得写入 Economic Substance：

```text
合同金额 × 履约比例
计价公式计算结果
Actual Settlement 推导结果
Rule Engine 分摊结果
Tax Impact Result
```

如果需要通过公式、比例、结算或 Rule Engine 才能得到 component 金额：

```text
amount = null
```

计算结果留在 Rule Engine Output / Tax Impact Result，不回写 Economic Substance。

---

# 二十一、统一 Temporal RAG 输入

Temporal RAG 必须接收结构化检索条件。

至少包括：

```text
applicable_date
business_type
subject_type
economic_substance
tax_type
transaction_stage
```

根据场景可增加：

```text
contract_date
transaction_date
payment_date
performance_date
```

禁止仅把整份合同全文直接交给知识库检索。

---

# 二十二、统一法规 Metadata

法规库至少统一：

```text
law_id
title
document_no
issuer
tax_type
business_type
subject_type
valid_from
valid_to
article
source
version_status
```

字段一旦冻结不得随意修改。

---

# 二十三、统一法规时间规则

每条法规必须明确：

```text
valid_from
valid_to
```

仍有效法规统一：

```text
valid_to = null
```

项目不得混用 `null` 与 `9999-12-31`。

Temporal RAG 必须按交易适用时间选择有效法规版本。

---

# 二十四、统一 Regulation Result

Temporal RAG 输出必须结构化。

Regulation Result 至少包括：

```text
regulation_result_id
tax_type
judgement_item
legal_condition_text
legal_conditions[]
value
legal_basis_ids[]
```

法规节点本身仍应可追溯：

```text
law_id
title
document_no
article
valid_from
valid_to
source
```

`legal_condition_text`：

```text
保存法规适用条件的可追溯文本
```

`legal_conditions[]`：

```text
保存能够稳定结构化的法律适用条件
```

每个条件可以区分：

```text
deterministic_condition
semantic_condition
```

能结构化判断的条件优先输出：

```text
fact_path
operator
expected_value
```

无法稳定结构化的复杂法律条件可以保留为 semantic condition。

`value` 表示：

```text
当 legal_conditions 成立时，该法规规定的结构化法律结论
```

Regulation Result 只提供法规层面的候选法律结论和适用条件，不直接宣布当前 Case 已满足条件。

具体适用性由 Rule Engine 结合当前 Facts 判断。

Rule 本身不固定保存具体 `legal_basis_ids[]`，本次实际法规依据由 Regulation Result 提供。

---

# 二十五、统一 Tax Judgement 定位

一个 Tax Case 只生成一个整体：

```text
tax_judgement
```

整体、模块、原子判断项统一使用：

```text
confirmed
partial
unknown
not_applicable
```

当前正式链路：

```text
Transaction Facts
+
Economic Substance
+
Regulation Result
+
Evidence / Consistency 等结构化输入
↓
Atomic Rule Execution
↓
Judgement Resolution Results
↓
Tax Judgement
```

Tax Judgement 主要消费已经收敛后的 `judgement_resolution_results[]`，并继承最终：

```text
value
legal_basis_ids[]
fact_basis_ids[]
```

Tax Judgement：

- 不创造事实；
- 不创造法规；
- 不直接生成正式 Risk Event；
- 不直接扣 Tax Health Score；
- 不直接扣 Evidence Coverage；
- 不保存最终 tax payable；
- 不反向修改上游对象。

---

# 二十六、统一 Tax Judgement 模块

预定义顶层模块：

```text
vat
surtax
corporate_income_tax
individual_income_tax
withholding_obligation
invoice_obligation
tax_timing
tax_preference
tax_filing_payment
```

LLM 根据当前 Tax Case 动态选择需要生成的模块。

LLM 不允许生成预定义集合之外的顶层模块。

某模块一旦生成，必须使用固定内部模板。

---

# 二十七、统一 Tax Judgement 原子项

普通原子判断项统一：

```json
{
  "status": "confirmed | partial | unknown | not_applicable",
  "value": null,
  "legal_basis_ids": [],
  "fact_basis_ids": []
}
```

规则：

## confirmed

```text
完整可靠可用结论
legal_basis_ids >= 1
fact_basis_ids >= 1
```

## partial

```text
至少已有部分可靠可用结果
legal_basis_ids >= 1
fact_basis_ids >= 1
```

`value` 直接保存已确认部分，不新增 `partial_value`。

## unknown

原则上：

```text
value = null
```

basis 可为空。

## not_applicable

```text
value = null
legal_basis_ids >= 1
fact_basis_ids >= 1
```

不新增 `unknown_reason`。

---

# 二十八、统一 Tax Judgement 依据追溯

`legal_basis_ids`：

- 来自本次 Temporal RAG / Regulation Result 实际命中的法规节点；
- 由支持最终结论的 Judgement Resolution Result 汇总；
- 不允许绕开 RAG。

`fact_basis_ids`：

- 原则上指向支持最终结论的 Transaction Facts；
- 不指向 LLM 推测；
- 不指向 Final Report；
- 不指向 Rule Engine 推导值本身。

`judgement_resolution_results[]` 必须直接汇总最终使用的：

```text
legal_basis_ids[]
fact_basis_ids[]
supporting_rule_execution_ids[]
```

Tax Judgement 直接继承，不在生成报告时重新搜索或重新汇总依据。

---

# 二十九、统一 Applicability 传播

## confirmed + true

正常继续下游判断。

## confirmed + false

```text
module.status = not_applicable
```

依赖项自动：

```text
status = not_applicable
value = null
```

并继承 applicability 的 basis。

## unknown

阻断依赖项：

```text
status = unknown
value = null
```

## partial

value 必须表达：

```json
{
  "applicable_components": [],
  "unresolved_components": []
}
```

已确认适用 component 可继续下游判断。

---

# 三十、统一 Tax Judgement component 规则

当前允许按 `substance_code` 分项的原子项：

```text
taxable_activity
taxable_amount
tax_rate
levy_rate
income_type
taxable_income_basis
invoice_details
invoice_amount_basis
```

以下原则上保持模块级单一结果：

```text
taxpayer
filing_obligation
payment_obligation
filing_deadline
payment_deadline
```

不新增 `component_id`。

同一原子项的 `details[]` 中：

```text
同一 substance_code 最多出现一次
```

detail 不单独增加 status。

当 details 使用时，每个 detail 自己保存：

```text
legal_basis_ids
fact_basis_ids
```

外层不重复保存。

---

# 三十一、统一 treatment_scope

同一 `substance_code` 如需多种税务处理，使用：

```text
treatments[]
```

每个 treatment 使用：

```json
{
  "treatment_scope": {
    "scope_type": "...",
    "scope_value": "..."
  }
}
```

`scope_type` 统一由 Scope Type Registry 管理。

每个 scope type 必须定义：

```text
scope_description
scope_value_schema
```

未登记 scope type 不得进入正式输出。

---

# 三十二、统一 VAT Tax Judgement

VAT 固定判断项：

```text
status
applicability
taxpayer
taxable_activity
taxable_amount
tax_rate
levy_rate
filing_obligation
payment_obligation
filing_deadline
payment_deadline
```

统一规则：

- `taxable_activity` 为 VAT 税法口径分类；
- `taxable_amount` 为 VAT 税法计税依据；
- `tax_rate` 与 `levy_rate` 分开；
- Tax Judgement 不保存 VAT 应纳税额；
- VAT 应纳税额由下游确定性计算；
- VAT 时点统一进入 `tax_timing`；
- VAT 优惠统一进入 `tax_preference`。

---

# 三十三、统一 Surtax 特殊两阶段规则

Surtax 固定判断项：

```text
status
applicability
taxpayer
taxable_basis
applicable_rate
filing_obligation
payment_obligation
filing_deadline
payment_deadline
```

执行：

```text
第一阶段 VAT Tax Judgement
↓
确定性计算 VAT 应纳税额
↓
confirmed VAT payable > 0
→ 生成 surtax

confirmed VAT payable = 0
→ 不生成 surtax

VAT payable 尚未确认
→ 暂不生成 surtax
```

当前两阶段机制只用于明确存在确定性计算依赖的模块，目前明确为 surtax。

---

# 三十四、统一 Corporate Income Tax

固定判断项：

```text
status
applicability
taxpayer
income_type
taxable_income_basis
applicable_tax_rate
filing_obligation
payment_obligation
filing_deadline
payment_deadline
```

业务边界：

- 只处理当前合同收入侧；
- 不计算企业全年完整应纳税所得额；
- 不扩展到全年成本、费用、亏损弥补；
- 删除 `deductibility_related_adjustment`；
- `applicable_tax_rate` 保存一般规则下基础税率；
- 税收优惠统一进入 `tax_preference`。

---

# 三十五、统一 Individual Income Tax

固定判断项：

```text
status
applicability
taxpayer
income_type
taxable_income_basis
applicable_tax_rate
withholding_relation
filing_obligation
payment_obligation
filing_deadline
payment_deadline
```

当前只处理本合同收入，不计算自然人全年完整综合所得结果。

税率 value 统一支持：

```json
{
  "rate_type": "proportional | progressive",
  "rate": null,
  "rate_table_id": null
}
```

---

# 三十六、统一 Withholding Obligation

固定判断项：

```text
status
applicability
withholding_agent
withheld_tax_type
withholding_basis
withholding_rate
filing_obligation
payment_obligation
filing_deadline
payment_deadline
```

`withholding_time` 统一进入：

```text
tax_timing.withholding_time
```

扣缴税额由下游确定性计算。

---

# 三十七、统一 Invoice Obligation

固定判断项：

```text
status
applicability
invoice_issuer
invoice_details
invoice_amount_basis
```

`invoice_details.value`：

```json
[
  {
    "invoice_type": "...",
    "invoice_item": "..."
  }
]
```

`invoice_amount_basis.value`：

```json
{
  "transaction_amount": 0,
  "currency": "CNY",
  "details": [
    {
      "invoice_type": "...",
      "invoice_item": "...",
      "invoice_amount_basis": 0
    }
  ]
}
```

规则：

- transaction_amount 必须复制自已确认 Facts；
- Tax Judgement 不得修改该原始金额；
- amount details 与 invoice_details 不强制一一对应；
- 只有金额已确认的项目进入 amount details；
- 不保存 `invoice_recipient`；
- 开票时间统一进入 `tax_timing.invoice_time`。

---

# 三十八、统一 Tax Timing

固定：

```text
status
vat_tax_liability_time
corporate_income_recognition_time
individual_income_tax_time
withholding_time
invoice_time
```

不保存：

```text
filing_time
payment_time
```

申报和缴纳期限保留在对应税种 / 扣缴模块。

---

# 三十九、统一 Tax Preference

顶层：

```text
status
preferences[]
```

每个 preference：

```text
tax_type
preference_type
eligibility_status
preference_rate
effective_period
```

规则：

- 模块级不增加 applicability；
- 同一 Tax Case 可有多项优惠；
- 单个 preference 不增加整体 status；
- 不增加 detailed eligibility_conditions；
- 不增加 preference_amount_basis；
- 详细优惠条件留在 Regulation Result；
- 符合优惠但未享受，不形成正式 Health Risk；
- 错误享受优惠可以形成正式 Risk Event。

---

# 四十、统一 Tax Filing Payment

顶层汇总模块只负责复制：

```text
filing_obligation
payment_obligation
filing_deadline
payment_deadline
```

可动态包含：

```text
vat
surtax
corporate_income_tax
individual_income_tax
withholding
```

只包含当前已经生成的对应模块。

该模块：

- 不重新判断；
- 不重新计算；
- 不创造新结论。

---

# 四十一、统一 partial 下游使用规则

Rule Engine 不读取“已经生成的 Tax Judgement”再反向执行规则。

正确顺序：

```text
Facts / Economic Substance / Evidence / Consistency / Regulation Result
↓
Atomic Rule
↓
Judgement Resolution
↓
Tax Judgement
```

当上游事实只确认一部分时，Atomic Rule 可以使用已确认的可靠部分。

例如：

```text
known_amount = 60000
total_amount = null
```

对于规则：

```text
amount > 50000
```

已确认下限已经足以证明成立时：

```text
confirmed_triggered
```

统一：

```text
已知部分足以证明成立 / 不成立
→ confirmed_triggered / confirmed_not_triggered

只能形成方向
→ provisional_triggered / provisional_not_triggered

无法形成可靠方向
→ unknown
```

禁止形成 Tax Judgement → Rule Engine → Tax Judgement 的循环依赖。

# 四十二、统一 Consistency Check

Consistency Check **只比较**：

```text
Contract Facts
↕
Actual Facts
```

不负责比较合同 / 实际与税法正确处理。

采用最小比较项粒度：

```text
一个具体比较项
→ 一条 Consistency Check Result
```

统一状态：

```text
consistent
partial
inconsistent
unknown
needs_review
```

检查方法：

```text
structured_check
semantic_check
```

`structured_check` 用于金额、数量、日期、税率、发票类型、标准化枚举等可确定比较项。

`semantic_check` 用于履约内容、验收内容、结算内容等复杂文本；无法可靠判断时输出 `needs_review`。

当一个 Contract Fact 对应多个 Actual Facts 时，允许在：

```text
归属明确
币种 / 单位兼容
不存在 unresolved possible_duplicate
```

的前提下先确定性聚合 Actual Facts 再比较。

聚合值只存在于 Consistency Check 运行结果，不回写 Actual Facts。

若相关 Actual Facts 位于尚未解决的 `duplicate_group`：

```text
→ 禁止简单累计
→ 相关累计比较 = unknown / needs_review
```

没有对应 Actual Fact 且证据不足时，不得直接判 `inconsistent`。

Consistency Check 不直接修改 Tax Health Score 或 Evidence Coverage。

# 四十三、统一 Rule 结构原则

Rule 采用 Atomic Rule 粒度：

```text
一条 Rule
→ 只判断一个最小 Tax Judgement 原子结论
```

每条 Rule 至少包含：

```text
rule_id
rule_domain
target_judgement_item
conditions[]
evidence_requirement_group_ids[]
rule_result_status
version
```

Rule 的 `conditions[]` 允许：

```text
deterministic_condition
semantic_condition
```

执行原则：

```text
能由结构化字段判断
→ deterministic_condition

确实无法结构化
→ semantic_condition

deterministic 结果优先
LLM semantic condition 不得覆盖已经明确的确定性结果
```

Rule 本身：

- 不保存法规有效期；
- 不固定绑定具体 `legal_basis_ids[]`；
- 法规时间适用与具体依据由 Temporal RAG / Regulation Result 提供。

多条 Atomic Rule 可以指向同一个 `target_judgement_item`，最终在 Judgement Resolution 层合并。

Rule 必须结构化，不允许仅用自然语言口头描述作为正式规则。

---

# 四十四、统一 Rule ID

每条 Rule 必须有唯一 `rule_id`。

Rule ID：

- 不重复；
- 正式使用后不随意改名；
- 删除后不复用旧 ID；
- 历史 alias 只能直接映射到当前 ID；
- 禁止 alias 链。

Risk Event ID 同样永久保留历史占用，不允许旧 ID 被新业务事件复用。

---

# 四十五、统一 Rule 结果状态

Rule Engine 统一输出：

```text
confirmed_triggered
confirmed_not_triggered
provisional_triggered
provisional_not_triggered
unknown
```

同一 Tax Judgement 原子项存在多条 Rule 时：

```text
confirmed
> provisional
> unknown
```

相反 provisional 结果不得阻止明确 confirmed 结果进入最终 resolution，但 provisional 执行记录必须保留。

如果存在彼此冲突的 confirmed 结果：

```text
resolution_status = conflict
```

不得静默选择一条。

如果只有 provisional 结果且彼此冲突，或现有规则 / 事实不足：

```text
resolution_status = insufficient / conflict
```

不得强行形成确定 Tax Judgement。

正式风险与 Tax Health Score 只使用最终确认成立的正式风险，不使用 provisional / unknown 直接扣分。

---

# 四十六、统一 AND Evidence Rule

严格 AND：

```text
先排除 not_applicable
```

然后：

```text
存在明确 missing / confirmed_triggered
→ confirmed_triggered

没有 missing，但存在 unknown
→ unknown

全部满足
→ confirmed_not_triggered

排除 not_applicable 后为空
→ confirmed_not_triggered
```

典型：

```text
provided + missing
→ confirmed_triggered

provided + unknown
→ unknown

missing + unknown
→ confirmed_triggered
```

---

# 四十七、统一 OR Evidence Rule

OR 规则先排除 `not_applicable`。

然后：

```text
任一 provided
→ confirmed_not_triggered

全部 missing
→ confirmed_triggered

missing + unknown
→ provisional_triggered

全部 unknown
→ unknown

排除后为空
→ confirmed_not_triggered
```

一条 Evidence Rule 不允许混合 AND 与 OR。

复杂条件应拆成多个 Rule，再通过 Group 组合。

---

# 四十八、统一 Evidence Requirement Group

Evidence Requirement 来自固定：

```text
Evidence Requirement Registry
```

LLM 不得根据单个 Case 临时创造新的 Requirement 类型。

Evidence Requirement Group 可以根据当前合同与规则动态组合，但必须遵守：

- Group 只允许 AND；
- Group 不保留 `group_relation`；
- Group 不允许嵌套 Group；
- OR 关系在单个 Evidence Requirement / Evidence Rule 内处理；
- Group 只负责组合逻辑，不产生独立 Evidence State；
- Group 不配置 `configured_loss`；
- Group 不作为 Evidence Coverage 的额外评分对象。

Evidence State 只保存最小 Requirement Instance 的状态。

Evidence Coverage 的实际评分粒度统一为：

```text
Evidence Requirement Instance
```

同一：

```text
Requirement
+ target_object_id
+ period
```

只能有一个当前有效 Instance。多个 Rule / Group 触发同一 Instance 时，只合并 `trigger_source_ids[]`，不得重复扣分。

# 四十九、统一正式 Risk Event 定义

正式 Risk Event 必须经过：

```text
Judgement Resolution Result
+
Actual Facts / Tax Impact Result / Consistency Check 等已收敛结构化结果
↓
固定 Risk Trigger Rule
↓
confirmed_triggered
↓
Risk Event
```

Risk Trigger Rule 不能重新读取并解释原始合同、法规原文或底层证据。

Risk Trigger Rule 主要读取：

```text
Judgement Resolution Result
Tax Impact Result
Actual Tax Treatments
Actual Tax Filings / Tax Payments / Invoices / Withholdings
Actual Obligation States
Consistency Check
```

Risk Trigger Rule 只负责判断：

```text
已经确认的税务处理与实际执行是否满足某一种固定风险触发条件
```

LLM 不负责自由判断“是否构成正式风险”。

`provisional_triggered`：

```text
可作为待确认事项保留
但不生成正式 Risk Event
不进入 Tax Health Score
```

单纯 Evidence missing / unknown 不生成正式 Risk Event。

Agent 自身判断错误属于系统质量问题，不得形成用户 Tax Health 风险。

---

# 五十、统一 Risk Event 粒度

Risk Trigger Rule 采用最小风险类型：

```text
一条 Risk Trigger Rule
→ 一种明确 Risk Event
```

不同 Tax Judgement 原子判断项原则上对应不同风险类型，例如：

```text
incorrect_invoice_type
incorrect_invoice_item
incorrect_invoice_amount
late_vat_filing
underpaid_vat
incorrect_vat_tax_rate
```

Risk Event 合并规则：

```text
同税种
+
同风险性质 / target_judgement_item
+
同 underlying cause
+
属于同一持续问题的连续期间
→ 合并一个 Risk Event
```

同税种、同问题、同根源同时影响多个 `substance_code`：

```text
→ 合并一个 Risk Event
→ substance_codes[] 可包含多个值
→ impact_scope 反映范围
```

不同税种：

```text
→ 不合并
```

即使 VAT、Surtax、CIT 来自同一业务根源，也分别生成税种级 Risk Event。

同一底层金额影响通过 `impact_group_id` 去重金额后果，不因为多个原子问题重复计算同一笔税差。

---

# 五十一、统一风险方向

以下事项原则上不形成正式 Tax Health Risk：

```text
多缴税
重复缴税但未形成其他合规风险
符合优惠条件但未享受优惠
```

可以进入：

```text
Tax Impact Result
Final Report
```

由于 Next Actions 当前只针对正式 confirmed Risk Event 生成，以上非正式风险事项不自动生成 Next Actions。

错误享受不应享受的税收优惠，可以形成正式 Risk Event。

---

# 五十二、统一 missing / late / incorrect / underpaid

申报：

```text
missing_*_filing
late_*_filing
incorrect_*_filing
```

缴纳：

```text
missing_*_payment
late_*_payment
underpaid_*
incorrect_*_payment
```

扣缴：

```text
missing_*_withholding
late_*_withholding
underwithheld_*
```

发票：

```text
missing_invoice
late_invoice
incorrect_invoice_type
incorrect_invoice_item
incorrect_invoice_amount
```

动态当前状态原则：

```text
missing
↓ 后续完成
missing 消失
↓
若逾期则出现 late
```

部分缴纳 / 部分扣缴后：

```text
missing
→ underpaid / underwithheld
```

时间风险与内容 / 金额风险允许并存。

---

# 五十三、统一税务时点风险

当前独立时点风险：

```text
incorrect_vat_tax_liability_time
incorrect_corporate_income_recognition_time
incorrect_individual_income_tax_time
incorrect_withholding_time
```

不建立：

```text
incorrect_invoice_time
```

发票时间问题统一由：

```text
missing_invoice
late_invoice
```

处理。

---

# 五十四、统一上游风险 suppression

统一采用：

```text
具体后果优先
```

适用于：

```text
economic_substance_inconsistency
*_obligation_not_applied
incorrect_*_taxable_activity
incorrect_*_income_type
未来类似上游原因风险
```

只有所有已识别相关下游后果都处于最终状态时，才允许 suppression 上游风险。

最终状态：

```text
confirmed_triggered
confirmed_not_triggered
明确 not_applicable
```

任一相关下游处于：

```text
provisional_triggered
provisional_not_triggered
unknown
```

则上游 Risk Event 继续保留。

suppression 必须根据当前最新结果动态重算。

此外：

```text
同一 underlying tax difference
→ 用 impact_group_id 标记同一金额影响

同一持续税务问题
→ 合并 Risk Event

不同税种
→ 不跨税种合并
```

---

# 五十五、统一同一 Risk Event 的多 Rule 聚合

Risk Event **不直接根据每条 Rule Execution 生成**。

正式链路：

```text
多个 Atomic Rule Execution
↓
Judgement Resolution Result
↓
Risk Trigger Rule
↓
Risk Event
```

同一个 Tax Judgement 原子项的多个 Rule Execution 必须先在 Judgement Resolution 层完成：

```text
一致结果合并
confirmed / provisional 优先级处理
confirmed 冲突保留 conflict
```

只有最终 resolution 已形成可确认风险条件时，Risk Trigger Rule 才能生成 Risk Event。

Risk Event 可以保留：

```text
related_judgement_resolution_ids[]
related_rule_execution_ids[]
```

用于追溯，但风险生成入口只认最终 resolution，避免一个问题被多条 supporting rules 重复生成风险。

---

# 五十六、统一 Tax Health Score 定位

Tax Health Score 只反映：

```text
当前已确认成立的正式税务风险严重程度
```

证据不足本身不得等量扣 Health Score。

只有：

```text
confirmed_triggered
```

可以形成正式 Health loss。

---

# 五十七、统一 Tax Health Score 五维

每个正式 Risk Event 固定使用：

```text
tax_consequence_severity
tax_amount_impact
obligation_violation_severity
duration_severity
impact_scope
```

全部：

```text
0 / 1 / 2 / 3 / 4
```

中央语义：

```text
0 = 无 / 不适用 / 当前无法确认该维度严重程度
1 = 低
2 = 中
3 = 高
4 = 很高
```

五个维度由固定：

```text
Scoring Rules / Mapping Tables
```

确定。

LLM 不得自由打分。

例如：

```text
税差金额区间
→ tax_amount_impact 固定映射

连续期间长度
→ duration_severity 固定映射

影响范围
→ impact_scope 固定映射
```

如果某个维度现有信息不足以可靠确定：

```text
该维度 = 0
```

其他已确认维度继续计算。

LLM 只能解释评分结果，不得修改评分。

---

# 五十八、统一 Health Score 权重与公式

权重：

```text
tax_consequence_severity       25%
tax_amount_impact              20%
obligation_violation_severity  30%
duration_severity              15%
impact_scope                   10%
```

公式：

```text
weighted_severity
=
tax_consequence_severity × 0.25
+ tax_amount_impact × 0.20
+ obligation_violation_severity × 0.30
+ duration_severity × 0.15
+ impact_scope × 0.10
```

```text
health_score_loss
=
weighted_severity × 10
```

单 Risk Event：

```text
health_score_loss = 0–40
```

允许小数。

Rule 配置不再人工保存：

```text
health_score_loss
risk_level
```

---

# 五十九、统一 Risk Level

由 `health_score_loss` 自动确定：

```text
0 <= loss < 5
→ low

5 <= loss < 15
→ medium

15 <= loss < 25
→ high

loss >= 25
→ critical
```

Risk Level 使用未取整的原始 loss 判断。

LLM、Final Report、人工展示层不得重新改 Risk Level。

---

# 六十、统一 final_risk_events

最终 Risk Event 至少包含：

```text
risk_event_id
risk_event_type
risk_event_name
tax_type
target_judgement_item
substance_codes[]
related_transaction_fact_ids[]
related_judgement_resolution_ids[]
related_tax_impact_ids[]
supporting_risk_trigger_rule_ids[]
impact_group_id
period_start
period_end
severity_scores
weighted_severity
health_score_loss
risk_level
```

连续期间、同根源、同税种、同风险性质的问题按统一合并规则形成一个 Risk Event。

排序：

```text
critical
> high
> medium
> low
```

同一风险等级：

```text
health_score_loss 从高到低
```

不设置第三排序条件。

# 六十一、统一 Tax Health Score 总分

```text
total_health_score_loss
=
Σ final_risk_events.health_score_loss
```

规则：

- 保留小数；
- 允许超过 100；
- 不封顶。

```text
raw_tax_health_score
=
max(0, 100 - total_health_score_loss)
```

最终：

```text
tax_health_score
=
floor(raw_tax_health_score)
```

不设置：

```text
overall_risk_level
A/B/C/D 等级
```

---

# 六十二、统一 Evidence Coverage 定位

Evidence Coverage 只反映：

```text
当前已经进入检查阶段的 Evidence Requirement Instances
有多少已经获得有效证据满足
```

Evidence Coverage 与 Tax Health Score 完全独立。

允许：

```text
Tax Health Score = 100
Evidence Coverage = 35
```

其含义只能是：

```text
当前已确认范围内未发现正式税务风险
但证据覆盖较低，仍存在较大未确认范围
```

Evidence Requirement 只允许在 Tax Judgement 前生成；Tax Judgement 后不反向追加新的 Requirement。

---

# 六十三、统一 Evidence Coverage 固定缺口模型

v0.5 正式废弃 Evidence Coverage 五维质量评分模型。

废弃：

```text
evidence_importance
evidence_completeness
evidence_directness
evidence_consistency
evidence_validity
weighted_quality
quality_gap
importance_factor
evidence_loss_multiplier
```

每个 `Evidence Requirement` 在 Registry 中固定配置：

```text
configured_loss
```

同一个 Requirement 在不同 Case、不同 target、不同 period 的 Instance 均继承同一 `configured_loss`，Instance 不允许运行时修改。

---

# 六十四、统一 Evidence State 扣分系数

Evidence State 对 Evidence Coverage 的统一系数：

```text
provided
→ state_factor = 0

unknown
→ state_factor = 0.5

missing
→ state_factor = 1

not_applicable
→ 不参与评分

未来未到 check_due_date、尚无 Evidence State 的 Instance
→ 不参与评分
```

每个 Instance：

```text
actual_evidence_coverage_loss
=
configured_loss × state_factor
```

`unknown = 50%` 为全项目统一系数，不允许单独 Rule 自定义。

---

# 六十五、统一 Evidence Coverage 评分粒度

Evidence Coverage 按：

```text
Evidence Requirement Instance
```

分别评分。

同一个 Requirement 应用于三个不同付款阶段：

```text
instance_001
instance_002
instance_003
```

均可分别产生 loss。

同一：

```text
Requirement
+ target_object_id
+ period_start / period_end
```

只能存在一个当前有效 Instance。

多个触发来源通过：

```text
trigger_source_ids[]
```

合并，不重复生成 Instance。

---

# 六十六、统一 Evidence Requirement Group 评分边界

Evidence Requirement Group 只负责：

```text
AND 组合逻辑
```

Group 不再配置：

```text
configured_loss
```

也不作为额外 Evidence Coverage 评分对象。

组内 Requirement 各自按 Instance 评分，避免 Group 与内部 Requirement 重复扣分。

OR 备选材料仍在单个 Evidence Requirement 内表达，不在 Group 中混合 AND / OR。

---

# 六十七、统一 Evidence Coverage 去重

Evidence Coverage 不按底层文件去重。

同一份材料可以支持多个不同业务 Evidence Requirement Instances。

真正需要去重的是：

```text
同一 Requirement
+ 同一 target
+ 同一期间
```

不得因多个 Rule 同时触发而生成多个 Instance 或重复扣分。

---

# 六十八、统一 Evidence Coverage 总分

```text
raw_total_evidence_coverage_loss
=
Σ actual_evidence_coverage_loss
```

```text
total_evidence_coverage_loss
=
min(100, raw_total_evidence_coverage_loss)
```

```text
raw_evidence_coverage
=
max(0, 100 - total_evidence_coverage_loss)
```

最终：

```text
evidence_coverage
=
floor(raw_evidence_coverage)
```

与 Health Score 区别：

```text
total_health_score_loss
→ 可以 > 100

total_evidence_coverage_loss
→ 封顶 100
```

---

# 六十九、统一 Evidence Coverage 输出明细

最终至少保存：

```text
evidence_coverage
total_evidence_coverage_loss
evidence_loss_details[]
```

每条 detail 至少：

```text
evidence_requirement_instance_id
evidence_requirement_id
evidence_state_id
state
configured_loss
state_factor
actual_evidence_coverage_loss
```

Final Report 可以解释，不得重算。

---

# 七十、统一 Evidence Coverage 与 Evidence State 边界

Evidence State 只表达：

```text
provided
missing
unknown
not_applicable
```

不增加：

```text
provided_strong
provided_partial
provided_weak
```

`provided` 表示当前有效材料已经满足该 Requirement Instance，因此 coverage loss = 0。

`provided` 不强制要求已经形成正式 Actual Fact，但：

```text
supporting_source_file_ids[] >= 1
```

`related_actual_fact_ids[]` 可以为空。


# 七十一、统一 Rule Engine 处理顺序

当前统一主流程：

```text
1. 创建 Tax Case，完成文件分类与合同文件角色识别
2. 提取 Contract Facts，并生成 Contract Fact Relations
3. 仅基于 Contract Facts 形成 Economic Substance
4. 提取 Actual Facts，并生成 Actual Fact Relations / Issues / Duplicate Groups
5. 根据 Registry 生成 Evidence Requirement Instances
6. 到检查时点后生成 Evidence States
7. 形成 Transaction Facts
8. 执行 Consistency Check（Contract ↔ Actual）
9. Temporal RAG 检索当期有效法规
10. 输出结构化 Regulation Results
11. 组装 Rule Engine Input
12. 执行 Atomic Rules
13. 保存 rule_execution_results[]
14. 聚合同一 target_judgement_item，生成 judgement_resolution_results[]
15. 形成 Tax Judgement
16. 执行确定性 Tax Impact 计算
17. 运行固定 Risk Trigger Rules
18. 生成、合并并 suppression Risk Events
19. 通过固定 Mapping Tables 计算 Tax Health Score
20. 按 Evidence Requirement Instance 计算 Evidence Coverage
21. 基于正式 Risk Event 生成 Next Actions
22. 生成 Final Report
23. 全部核心模块完成后组装 agent_schema.json
```

Rule Engine Input 除交易组件层引用外，必须能够单独读取：

```text
actual_tax_filing_refs[]
actual_tax_payment_refs[]
```

用于 Tax Case + tax_type + period 级实际申报、缴税判断。

Surtax 的 VAT 前置税额依赖继续按 Tax Judgement 特殊两阶段规则执行。

# 七十二、统一 Rule Engine 权限边界

Rule Engine 负责：

```text
确定性条件判断
必要时受控 semantic_condition 判断
Atomic Rule 状态
Judgement Resolution
法规条件与 Facts 的适用性匹配
确定性税额 / 差额计算
Tax Impact Result
Risk Trigger Rule 执行
Risk Event 识别、聚合与 suppression
Tax Health Score
Evidence Coverage
Risk Level
Evidence Gaps / scoring details
```

Rule Engine 不负责：

```text
创造新的交易事实
改写 Contract Facts / Actual Facts / Economic Substance
改写法规
猜测缺失事实
把 unknown 强行变成确定事实
静默解决 confirmed 规则冲突
```

所有下游结果不得反向改写上游对象。

---

# 七十三、统一 LLM 权限边界

LLM 可以：

```text
文件内容理解
Contract Facts 结构化提取
Actual Facts 结构化提取
文件角色 / 结构化关系候选识别（必须受既定规则约束）
Economic Substance 分类（仅基于 Contract Facts）
Consistency Check semantic_check
Rule 中必要的 semantic_condition
Tax Judgement 整体 / 模块综合表达
基于 confirmed Risk Event 生成 Next Actions
Final Report 的解释与组织
```

LLM 不允许：

```text
把推断写成 Actual Facts
把推断写成 provided Evidence
仅凭金额相同、日期接近、顺序接近建立正式关系
使用 Actual Facts 反向改写 Economic Substance
修改 Tax Health Score
修改 Evidence Coverage
修改 Risk Level
自行新增 Risk Event
自行新增 Evidence Requirement
自行新增评分规则
修改 severity_scores
修改 configured_loss
修改 Evidence State state_factor
修改法规有效期
绕过 Rule Engine 重新做税务判断
在 Final Report 中重新计算评分或税额
下游直接修改上游对象
```

# 七十四、统一 Temporal RAG 权限边界

Temporal RAG 负责：

```text
根据 applicable_date 等结构化条件检索当期有效法规
提供法规条款
提供法规来源
提供法规节点 ID
结构化提取 legal_condition_text
结构化提取 legal_conditions[]
结构化提取法规条件成立时的 value
```

Temporal RAG 不负责：

```text
直接宣布当前 Case 已满足法规条件
直接扣 Health Score
直接扣 Evidence Coverage
决定最终 Risk Level
创造交易事实
```

当前 Case 是否满足法规适用条件由 Rule Engine 结合 Facts 判断。

---

# 七十五、统一 Final Report

Final Report 必须读取已经确定的上游对象。

至少包括：

```text
合同基本情况
Economic Substance
实际履约情况
Tax Judgement
Consistency Check
已确认税务风险
待确认事项
无法判断事项
证据不足
Tax Impact
Tax Health Score
Evidence Coverage
法规依据
Next Actions
```

报告必须严格区分：

```text
已确认税务风险
→ 只来自正式 Risk Event

待确认事项
→ provisional / partial / needs_review 等

无法判断事项
→ unknown / unresolved conflict 等

证据不足
→ Evidence State missing / unknown + Evidence Coverage
```

存在 `conflict / needs_review / unknown` 时仍然生成 Final Report，不阻断整个 Case。

Final Report 只能解释、总结和组织已有结构化结果，不得：

```text
新增税务结论
新增 Risk Event
新增税额
把 provisional / unknown 升级为 confirmed
重新计算 Tax Health Score
重新计算 Evidence Coverage
修改 Risk Level
修改 Risk Event ID / Name
修改 Rule 状态
修改法规有效期
```

# 七十六、统一 Risk Event Registry

每个 Risk Event 至少维护：

```text
risk_event_id
risk_event_name
description
parent_risk_event_ids
suppressed_parent_risk_event_ids
version
```

原则：

- ID 为纯业务语义 snake_case；
- name 由 Registry 统一定义；
- Final output 复制正式 name；
- description 保留在 Registry；
- 历史 ID 不复用；
- alias 只允许直接映射到当前 ID；
- 无法解析的历史 ID 记录非阻断错误并跳过当前风险聚合；
- 历史 ID 解析失败不得影响 Evidence Coverage。

---

# 七十七、统一当前状态与历史记录

正式评分只使用：

```text
当前最新事实
当前最新证据
当前最新 Regulation Result
当前最新 Tax Judgement
当前最新 Rule Engine Output
```

历史 Rule Output 不参与当前评分。

missing / late / underpaid 等风险根据当前状态动态重新计算。

---

# 七十八、统一 Tax Impact Result

Tax Impact Result 按“每一个产生金额后果的已收敛税务判断”单独生成，不先按税种汇总。

每条至少可包含：

```text
tax_impact_result_id
impact_group_id
tax_type
substance_code
target_judgement_item
tax_base_amount
expected_tax_amount
actual_tax_amount
tax_difference_amount
related_judgement_resolution_ids[]
fact_basis_ids[]
legal_basis_ids[]
```

原则：

```text
只保存能够确定计算出的金额
```

如果计税基础、税率或关键事实仍不确定：

```text
对应金额字段 = null
```

不得为了风险评分估算潜在税额。

同一 underlying tax difference 被多个判断项发现时：

```text
使用同一 impact_group_id
```

用于避免同一笔金额后果重复计入风险影响。

多缴、未享受优惠等事项可以进入 Tax Impact Result，即使不形成正式 Health Risk。

---

# 七十九、统一 Next Actions

Next Actions **只针对正式 confirmed Risk Event 生成**。

以下事项不单独生成 Next Actions：

```text
provisional_triggered
Evidence State missing / unknown
Consistency Check unknown / needs_review
Tax Judgement partial / unknown
单纯证据不足
```

Next Actions 的生成方式：

```text
confirmed Risk Event
+
对应 Tax Judgement
+
Tax Impact Result
+
legal_basis_ids / fact_basis_ids
↓
LLM 生成针对当前 Case 的整改行动
```

当前不建立固定“风险类型 → Action 模板库”。

LLM 允许：

```text
根据已确认 Risk Event 组织具体整改步骤
引用已有税种、期间、金额、法规依据
```

LLM 不允许：

```text
新增 Risk Event
把待确认事项升级为正式风险
自行新增上游未确认税额
重新做 Tax Judgement
```

---

# 八十、统一模块输入输出

每个模块必须明确：

```text
输入是什么
输出是什么
缺字段怎么办
出错怎么办
```

每个模块必须有：

```text
Input Schema
Output Schema
Error Handling
Mock Input
Mock Output
```

---

# 八十一、统一技术错误返回

统一建议：

```json
{
  "success": false,
  "error_code": "",
  "error_message": "",
  "failed_stage": ""
}
```

不同节点不得各自定义完全不同的错误格式。

---

# 八十二、统一 Mock JSON

至少准备：

```text
tax_case_mock.json
contract_facts_mock.json
actual_facts_mock.json
economic_substance_mock.json
evidence_requirement_mock.json
evidence_requirement_instance_mock.json
evidence_state_mock.json
transaction_facts_mock.json
consistency_check_mock.json
regulation_result_mock.json
rule_engine_input_mock.json
rule_engine_output_mock.json
tax_judgement_mock.json
tax_impact_result_mock.json
final_risk_events_mock.json
tax_health_score_mock.json
evidence_coverage_mock.json
next_actions_mock.json
final_report_mock.json
```

Mock 的作用：

- 上游未完成时下游仍可开发；
- 提前测试接口；
- 提前发现字段冲突；
- 减少三人相互等待。

---

# 八十三、统一 Golden Test Cases

三人必须共用一套 Golden Test Cases。

每个完整 Case 至少保存关键业务断言：

```text
输入文件及文件分类结果
预期 Tax Case / source_files
预期 Contract Facts / contract_fact_relations
预期 Actual Facts / actual_fact_relations
预期 actual_fact_issues / duplicate_groups
预期 Economic Substance
预期 Evidence Requirement Instances / Evidence States
预期 Transaction Facts
预期 Consistency Check
预期 Regulation Result
预期 Rule statuses / Judgement Resolution
预期 Tax Judgement
预期 Tax Impact
预期 Risk Events
预期 Tax Health Score
预期 Evidence Coverage
预期报告重点
```

Golden Test 锁定关键业务断言，不要求 LLM 最终自然语言逐字一致。

必须覆盖：

```text
文件分类失败但 Case 可继续
主合同 + 补充 / 变更协议覆盖
contract_fact_issues
单阶段 term / 多阶段 term + stages
stage 继承与 null 阻断继承
contract_fact_relations
Actual 多材料同一事件
possible_duplicate / duplicate_group
Actual ↔ Contract term / stage 回退关联
Evidence future Instance 无 State
working_day check_due_date
provided / missing / unknown Evidence Coverage 系数
uncertain Economic Substance
同 substance_code 独立 Components
Transaction Fact 组装
Consistency 聚合与 duplicate 阻断
Rule confirmed / provisional / conflict
Risk Trigger / Risk suppression
Health Score 边界
Evidence Coverage 边界
Final Report 在 unknown / conflict 下仍生成
```

# 八十四、统一版本管理

当前统一原则版本：

```text
v0.5
```

以下资产必须有版本：

```text
Schema
Enums / Registries
Prompt
Economic Substance Registry
Scope Type Registry
Risk Event Registry
Evidence Requirement Registry
Regulations Metadata
Temporal RAG Rules
Tax Judgement Rules
Consistency Check Rules
Risk Trigger Rules
Evidence Rules
Scoring Rules
Rule Engine
Dify Workflow
Golden Test Cases
```

建议：

```text
v0.1
v0.2
v0.3
v0.4
v0.5
v0.6
v1.0
```

Registry 文件本身可以版本化用于变更记录，但 Tax Case **不锁定 Registry 旧版本**：

```text
Registry 更新
→ 新 Case 使用最新版
→ 旧 Case 重新运行时也使用最新版
```

不得静默保留旧 Case 的历史 Registry 判断作为当前结果。

---

# 八十五、v0.5 主要变更

相对 v0.4，v0.5 主要新增或替换：

1. 一个 Tax Case 固定对应一个核心合同关系；
2. 正式增加 `module_statuses`，`case_status` 改为确定性派生；
3. 文件分类失败的材料不进入 `source_files[]`，单文件失败原则上不阻断 Case；
4. Case 内核心业务对象 ID 全局唯一，并在重跑时尽量保持稳定；
5. 稳定 ID 优先依赖 `object_type + source_file_id + source_page + source_text/source_anchor`；
6. Contract Facts 采用“未涉及字段可省略、涉及但未知写 null”的结构；
7. 新增 `contract_fact_issues[]`；
8. Payment / Invoice / Performance / Acceptance 支持 `term + optional stages[]`；
9. 多阶段时 stage 为最小执行 / 比较单位，单阶段时 term 自身为最小单位；
10. 父子结构采用“字段缺失继承、null 阻断继承、非空覆盖”；
11. Contract Facts 跨对象关系集中到 `contract_fact_relations[]`；
12. 新增 `Contract Fact Relation Type Registry`；
13. Actual↔Contract 对应集中到 `actual_fact_relations[]`；
14. 新增 `actual_fact_issues[]` 与 `duplicate_groups[]`；
15. Evidence Requirement Instance 改为 `target_object_id + trigger_source_ids[]`；
16. future Instance 可提前生成，但未到期无 Evidence State、不评分；
17. `check_due_date` 允许根据已确认触发事件做确定性计算；
18. working_day 使用合同定义优先、Calendar Registry 兜底；
19. Evidence Coverage 五维模型正式废弃，改为 `configured_loss × state_factor`；
20. Evidence Group 不再额外评分；
21. Transaction Facts 增加 `economic_substance_ref`，引用 stage 时同时引用父 term；
22. 同一 substance_code 在独立交易链下允许多个 Economic Substance Components；
23. Economic Substance 改为 `contract_fact_refs[]` 追溯，不再重复 sources；
24. Rule Engine → Judgement Resolution → Tax Judgement 的单向关系进一步冻结；
25. Root Schema 仅代表完整最终 Case，且只有 Root 保存 `schema_version`；
26. 所有顶层模块必须携带 `tax_case_id`；
27. Root 最终保留 `rule_engine_input` 以支持审计追溯。

# 八十六、正式废弃规则

以下旧设计不得继续实现：

```text
用户自然语言事实补充入口
```

```text
未分类文件以 source_file_type = unknown 进入正式 source_files[]
```

```text
Contract Facts / Actual Facts 依赖大量 related_*_ids[] 双向关系
```

```text
单阶段 term 也强制制造 stage
```

```text
stage 递归嵌套 sub_stages[]
```

```text
stage = null 时继续继承父 term
```

```text
LLM 仅凭金额相同、日期接近、名称相似建立正式跨对象关系
```

```text
同一 substance_code 在任何情况下都强制只有一个 Economic Substance Component
```

```text
Economic Substance 重复保存 sources[]
```

```text
Evidence Coverage 五维：
evidence_importance
evidence_completeness
evidence_directness
evidence_consistency
evidence_validity
weighted_quality
quality_gap
importance_factor
evidence_loss_multiplier
```

```text
Evidence Requirement Group 独立产生 coverage loss
```

```text
provided Evidence 继续产生质量扣分
```

```text
Tax Judgement → Rule Engine → Tax Judgement 循环依赖
```

```text
Risk Event 直接由每条 Rule Execution 生成
```

```text
证据 missing 直接形成正式 Tax Health Risk
```

```text
LLM / RAG / Final Report 反向创造 Actual Facts 或 Evidence State
```

# 八十七、统一 Change Log

项目统一维护：

```text
CHANGELOG.md
```

每次关键修改记录：

```text
修改日期
修改人
修改内容
修改原因
影响模块
是否更新 Schema
是否更新 Mock
是否更新 Golden Test
是否需要重新测试
```

凡修改：

```text
字段
枚举
Rule status
评分公式
Risk Event ID
Evidence Group
Tax Judgement 模块
Registry
```

都必须进入 Change Log。

---

# 八十八、统一 Git 目录

建议目录：

```text
tax-agent/
├── schemas/
│   ├── agent_schema.json
│   ├── tax_case_schema.json
│   ├── contract_facts_schema.json
│   ├── actual_facts_schema.json
│   ├── economic_substance_schema.json
│   ├── evidence_schema.json
│   ├── transaction_facts_schema.json
│   ├── consistency_check_schema.json
│   ├── regulation_result_schema.json
│   ├── rule_schema.json
│   ├── rule_engine_input_schema.json
│   ├── rule_engine_output_schema.json
│   ├── tax_judgement_schema.json
│   ├── tax_impact_result_schema.json
│   ├── risk_event_schema.json
│   ├── scoring_schema.json
│   ├── next_actions_schema.json
│   └── final_report_schema.json
├── enums/
├── prompts/
├── regulations/
├── metadata/
├── registries/
├── rules/
│   ├── tax/
│   ├── risk/
│   ├── evidence/
│   └── consistency/
├── rule_engine/
├── scoring/
├── dify/
├── mocks/
├── tests/
├── docs/
└── CHANGELOG.md
```

Schema 正式采用：

```text
模块化子 Schema
+
agent_schema.json Root Schema
```

`agent_schema.json` 只负责统一引用与组合，不复制各模块定义。

`registries/` 至少包含：

```text
economic_substance_registry
tax_type_registry
invoice_type_registry
evidence_requirement_registry
contract_fact_relation_type_registry
working_day_calendar_registry
scope_type_registry
risk_event_registry
shared_enum_registries
```

---

# 八十九、统一文件命名

项目文件统一使用：

```text
lower_snake_case
```

例如：

```text
contract_facts_schema.json
tax_judgement_schema.json
risk_event_registry_v1.json
tax_health_score_rules_v1.md
evidence_coverage_rules_v1.md
workflow_v1.yaml
```

禁止使用：

```text
最终版
最终版2
真的最终版
new
new2
latest
latest_final
```

---

# 九十、统一 Prompt 管理

Prompt 不得只保存在 Dify 节点中。

正式 Prompt 必须同步保存到 Git，例如：

```text
/prompts/contract_facts_prompt_v1.md
/prompts/actual_facts_prompt_v1.md
/prompts/economic_substance_prompt_v1.md
/prompts/tax_judgement_prompt_v1.md
/prompts/final_report_prompt_v1.md
```

任何影响输出 Schema 的 Prompt 修改都必须更新版本和 Change Log。

---

# 九十一、统一优先级

发生冲突时，按以下优先级处理：

```text
1. 最新版本统一原则
2. 最新正式 Schema / Registry / Rule / Scoring Table
3. 最新正式业务规则文档
4. Golden Test 预期
5. Prompt
6. Dify 节点配置
7. 代码临时实现
8. 历史讨论记录
```

如果高低层发生冲突：

```text
先停止继续扩散
→ 更新统一定义
→ 更新受影响资产
→ 重跑 Golden Test
```

禁止为了迁就当前代码而偷偷修改业务含义。

任何下游模块发现上游对象可能错误：

```text
不得直接修改上游
→ 输出 unknown / needs_review / conflict
或
→ 重新运行对应上游节点
```

---

# 九十二、当前正式业务规则文件

截至 v0.6，以下四份既有正式业务文件仍是专项规则基础：

```text
01_tax_judgement_业务规则_v1.0.md
02_风险分类规则_v1.0.md
03_tax_health_score_评分维度_v1.0.md
04_evidence_coverage_评分维度_v1.0.md
```

其中 `04_evidence_coverage_评分维度_v1.0.md` 的旧五维模型已被 v0.5 的 `configured_loss × state_factor` 模型替代，必须同步升级专项文件后再用于开发。

但凡这些专项文件中的旧描述与 v0.6 已确认的：

```text
Facts / Evidence / Economic Substance
Rule Engine Output
Risk Trigger
Tax Impact
Next Actions
Final Report
Registry
Golden Test
Schema 组织
```

发生冲突，必须以本统一原则 v0.6 与后续最新正式 Schema / Rule / Registry 为准，并同步修订专项文件。

本统一原则负责约束：

```text
跨模块一致性
状态语义
权限边界
评分边界
Schema 变更流程
风险与证据聚合方式
团队交接标准
```

---

# 九十三、统一 Tax Case 核心 Schema

`Tax Case` 只保存 Case 元数据，不复制业务事实。

至少包含：

```text
tax_case_id
case_status
created_at
updated_at
module_statuses
source_files[]
```

不得在 Tax Case 重复保存：

```text
provider_name
customer_name
contract_number
contract_amount
contract_date
```

等 Contract Facts。

一个 Tax Case 只对应一个核心合同关系。

`source_files[]` 至少包含：

```text
source_file_id
source_file_name
source_file_type
contract_document_role   # 仅 contract 类文件需要
```

合同文件角色：

```text
main_contract
supplementary_agreement
amendment_agreement
```

正式 `source_files[]` 不允许 `source_file_type = unknown`。

所有顶层模块输出必须携带同一个：

```text
tax_case_id
```

Root 组装时必须校验一致。

核心业务对象 ID 在同一 Tax Case 内全局唯一。外部 `source_file_id`、法规知识库 `law_id / node_id` 等外部资源 ID 不纳入 Case 内业务对象 ID 唯一编号体系。

重跑稳定性：

```text
业务含义未变化的既有对象
→ 尽量沿用原 ID

新增对象
→ 新 ID

旧对象删除 / 失效
→ 原 ID 不复用给其他对象
```

稳定对象身份优先使用：

```text
object_type
+
source_file_id
+
source_page
+
source_text / source_anchor
```

进行匹配。

---

# 九十四、统一 Contract Facts 核心 Schema

Contract Facts 采用扁平顶层结构，不按税种嵌套。

顶层字段遵守：

```text
合同未涉及某事项
→ 对应字段 / 数组可以省略

合同涉及，但具体值无法可靠确认
→ 字段保留 = null
→ 必要时写入 contract_fact_issues[]

合同对象确实存在但部分属性未知
→ 允许生成 partial object
```

顶层标量不额外包装 Fact ID。

具有独立业务含义、可能多条存在的对象必须有全局唯一 ID。

## 94.1 Contract Fact Issues

统一异常容器：

```text
contract_fact_issues[]
```

至少支持：

```text
conflict
ambiguous
unreadable
missing_referenced_document
unresolved_amendment
```

每条至少可包含：

```text
issue_id
target_path
issue_type
candidate_values[]
source_file_ids[]
```

冲突只影响具体字段，不阻断整个 Contract Facts / Case。

## 94.2 合同变更合并

主合同 + 补充 / 变更协议形成一套当前有效 Contract Facts。

优先级：

```text
1. 文件明确的替代 / 废止 / 优先适用关系
2. effective_date
3. agreement / contract date
4. 仍无法判断 → unresolved / conflict，不猜
```

后续协议只覆盖明确修改部分；未修改内容继续沿用原合同。

## 94.3 Contract Content

`contract_content` 保存整体合同业务内容原文。

只有存在多个可独立区分的业务内容时才生成：

```text
contract_content_details[]
```

单一业务内容不为了关系建模强制创造 `content_detail`。

多个业务内容的 `content_detail` 可作为 `contract_fact_relations[]` 中的重要业务锚点。

## 94.4 term + optional stages[]

以下对象统一支持：

```text
payment_terms[]
invoice_terms[]
performance_terms[]
acceptance_terms[]
```

规则：

```text
单阶段
→ term 本身是最小执行 / 比较单位
→ 不生成 stages[]

多阶段
→ term 保存共同 / 默认属性
→ stages[] 保存各独立阶段
→ stage 为最小执行 / 匹配 / Consistency Check 单位
```

stage 拆分只需满足下列任一能够独立识别：

```text
业务内容
时间
金额
比例
触发条件
验收关系
付款关系
```

不要求每个 stage 都有独立金额。

stage 统一单层扁平，不允许 `sub_stages[]`。

每个 stage 有全局唯一 `*_stage_id`。

父子继承：

```text
stage 字段缺失
→ 继承 term

stage 字段存在且 = null
→ 明确未知，不继承

stage 字段有非空值
→ 覆盖 term
```

合同未直接写出的：

```text
总金额 × 比例
单价 × 数量
税率 × 税基
汇率换算
```

不得写回 Contract Facts。

## 94.5 Contract Fact Relations

所有 Contract Facts 跨对象关系统一集中保存：

```text
contract_fact_relations[]
```

每条至少：

```text
relation_id
source_object_id
target_object_id
relation_type
sources[]
```

只连接有 ID 的业务对象，不允许使用顶层字段路径作为 relation 节点。

同一关系只保存一次，不做双向重复写入。

`relation_type` 必须来自 `Contract Fact Relation Type Registry`，Registry 至少定义：

```text
relation_type
relation_description
allowed_source_object_types
allowed_target_object_types
direction_semantics
```

关系必须有合同文本直接依据。

禁止仅凭：

```text
金额相同
日期接近
出现顺序
名称相似
LLM 猜测
```

建立正式 relation。

允许 1:1、1:N、N:1、N:N 关系。

## 94.6 触发结构

统一：

```text
trigger_condition
trigger_events[]
trigger_logic
offset_days
day_type
```

`day_type`：

```text
calendar_day
working_day
null
```

相对期限不在 Contract Facts 中自动推导具体日期。

## 94.7 其他 Contract Terms

以下继续按既定业务规则保存：

```text
contract_amount / contract_amount_details[]
withholding_terms[]
tax_burden_terms[]
tax_compliance_terms[]
adjustment_terms[]
expense_terms[]
exchange_rate_terms[]
agency_terms[]
pricing_terms[]
settlement_terms[]
```

所有明确业务对象继续遵守“只保存合同直接表达内容、不写入后续计算结果”的原则。

---

# 九十五、统一 Actual Facts 核心 Schema

Actual Facts 按业务类型保存：

```text
actual_payments[]
actual_invoices[]
actual_performances[]
actual_acceptances[]
actual_settlements[]
actual_pricing_bases[]
actual_expenses[]
actual_adjustments[]
actual_agency_transactions[]
actual_withholdings[]
actual_tax_filings[]
actual_tax_payments[]
```

对象存在 = 当前材料已观察到该实际事件。

对象不存在 ≠ 自动等于事件未发生。

只要事件本身能够确认发生，即使部分属性冲突 / 未知，也保留 Actual Fact；具体字段可为 null。

## 95.1 Actual Fact Relations

所有 Actual↔Contract 对应统一集中到：

```text
actual_fact_relations[]
```

每条至少可包含：

```text
relation_id
actual_fact_id
contract_fact_id
relation_type
allocated_amount
currency
sources[]
```

该关系表只负责：

```text
Actual Fact ↔ Contract Fact
```

不负责 Actual↔Actual 关系。

能明确到 stage：

```text
→ 优先关联 stage
```

只能确认属于整套安排：

```text
→ 允许退回关联父 term
```

无法确认金额分配时：

```text
allocated_amount = null
```

不得平均拆分或猜分。

`actual_tax_filings[]`、`actual_tax_payments[]` 可没有 Contract relation。

## 95.2 Actual Fact Issues

统一：

```text
actual_fact_issues[]
```

事件本身确认、具体字段冲突时：

```text
事件对象保留
冲突字段 = null
issue 记录 candidate_values / sources
```

## 95.3 Duplicate Groups

多份材料无法确认是同一事件还是不同事件时：

```text
不自动合并
不默认按多笔累计
```

建立：

```text
duplicate_groups[]
```

至少：

```text
duplicate_group_id
actual_fact_ids[]
```

未解决 duplicate group 内的 Actual Facts：

```text
不得直接累计金额 / 数量 / 次数
不得形成依赖该聚合值的 confirmed Tax Impact / Risk
```

只有存在可靠事件身份依据才允许合并多份材料为同一个 Actual Fact，例如：

```text
发票号码
交易流水号
税票编号
验收单编号
明确单据编号
材料直接互相引用
```

仅金额相同、日期接近、主体相同不足以证明同一事件。

## 95.4 一份材料多个事件

一份材料明确包含多个独立事件时，按事件拆多个 Actual Facts，同一 source 可以被多条 Actual Fact 引用。

一张发票仍是一个 `actual_invoice`，多行项目使用 `invoice_lines[]`。

---

# 九十六、统一 Evidence Requirement / Instance / State

## 96.1 Evidence Requirement Registry

Evidence Requirement 只能来自固定 Registry。

每个 Requirement 至少定义：

```text
evidence_requirement_id
purpose
accepted_source_file_types[]
configured_loss
```

`configured_loss` 固定在 Registry，不在 Instance 层动态修改。

OR 备选证据在单个 Requirement 内表达。

Evidence Requirement Group 只允许 AND，不独立评分。

## 96.2 Evidence Requirement Instance

每个 Instance 只对应一个最小业务目标：

```text
evidence_requirement_instance_id
evidence_requirement_id
target_object_id
trigger_source_ids[]
period_start
period_end
check_due_date
```

目标统一使用 `target_object_id`，不为不同业务类型创建多套 target 字段。

同一：

```text
Requirement
+ target_object_id
+ period
```

只生成一个当前有效 Instance；多个触发来源合并到 `trigger_source_ids[]`。

未来 Requirement 可以提前生成 Instance。

尚未到检查阶段：

```text
保留 Instance
不生成 Evidence State
不记 missing
不进入 Evidence Coverage
```

## 96.3 check_due_date

允许根据：

```text
合同 trigger 明确
+
实际触发事件已确认
+
offset_days 明确
+
day_type 明确
```

确定性计算 `check_due_date`。

该计算结果不写回 Contract Facts。

`working_day`：

```text
合同明确给出工作日定义
→ 合同定义优先

合同未定义
→ Working Day Calendar Registry
```

Calendar Registry 至少维护：

```text
calendar_date
is_working_day
holiday_name
year
source
```

Registry 不完整时不得猜工作日。

## 96.4 Evidence State

每个 Instance 在核心 Schema 中只保留一个当前最新 Evidence State：

```text
evidence_state_id
evidence_requirement_instance_id
state
related_actual_fact_ids[]
supporting_source_file_ids[]
```

一个 Evidence State 可由多份材料共同支持。

`provided`：

```text
supporting_source_file_ids[] >= 1
related_actual_fact_ids[] 可以为空
```

Evidence State 只表达：

```text
provided
missing
unknown
not_applicable
```

不表达证据质量等级。

---

# 九十七、统一 Transaction Facts 核心 Schema

每条至少：

```text
transaction_fact_id
economic_substance_ref
substance_code
contract_fact_refs[]
actual_fact_refs[]
evidence_state_refs[]
```

引用分层保存，不合并为统一 object refs。

`substance_code = null` 时仍可生成 Transaction Fact。

引用 stage 时必须同时引用对应父 term。

默认一个 Economic Substance Component 对应一个 Transaction Fact；只有结构化关系能够确认独立交易链时才拆分。

Transaction Facts 只组合引用，不复制金额、日期、税率等上游值。

---

# 九十八、统一 Economic Substance 核心 Schema

每个 component：

```text
substance_component_id
substance_code
classification_status
role
amount
currency
contract_fact_refs[]
```

不重复保存 `sources[]`。

同一 substance_code 在独立交易链下允许多个 Component。

Tax Judgement 仍按 substance_code 聚合；不同独立交易的差异税务处理通过 `treatments[] + treatment_scope` 表达。

---

# 九十九、统一 Consistency Check 核心 Schema

每条至少：

```text
consistency_check_id
contract_fact_refs[]
actual_fact_refs[]
comparison_item
check_method
status
```

`check_method`：

```text
structured_check
semantic_check
```

possible_duplicate 未解决时，禁止依赖简单聚合形成确定一致性结论。

---

# 一百、统一 Rule Engine Input / Output

## 100.1 Rule Engine Input

只保存引用，不复制上游事实值：

```text
tax_case_id
transaction_fact_refs[]
economic_substance_refs[]
consistency_check_refs[]
regulation_result_refs[]
evidence_state_refs[]
actual_tax_filing_refs[]
actual_tax_payment_refs[]
```

## 100.2 Rule Engine Output

固定两层：

```text
rule_execution_results[]
judgement_resolution_results[]
```

Atomic Rule Execution 保存每条规则执行结果。

Judgement Resolution 对同一 `target_judgement_item` 收敛：

```text
resolved
conflict
insufficient
```

confirmed 与相反 provisional 同时出现：

```text
confirmed 进入最终 resolution
provisional 保留追溯
```

confirmed vs confirmed 冲突：

```text
conflict
```

不得静默选一条。

Tax Judgement 只从 Judgement Resolution 形成。

---

# 一百零一、统一 Risk Trigger / Risk Event / Score Schema

Risk Event 不直接由 Rule Execution 生成。

正式链路：

```text
Judgement Resolution
+
Tax Impact / Actual / Consistency 等已收敛结构化结果
↓
固定 Risk Trigger Rule
↓
confirmed risk condition
↓
Risk Event
```

一条 Risk Trigger Rule 只对应一种最小 Risk Event 类型。

Risk Trigger 不能重新解释合同原文、法规原文或原始证据。

正式 Risk Event 至少可包含：

```text
risk_event_id
tax_case_id
risk_event_type
risk_event_name
tax_type
substance_codes[]
related_transaction_fact_ids[]
related_judgement_resolution_ids[]
related_tax_impact_ids[]
supporting_risk_trigger_rule_ids[]
impact_group_id
period_start
period_end
```

连续期间、同税种、同风险类型、同根源的问题按既定规则合并；不同税种不跨税种合并。

Tax Health Score 五维与权重继续采用已冻结规则。

某评分维度无法可靠确认：

```text
该维度 = 0
```

LLM 不参与自由打分。

---

# 一百零二、统一 Evidence Coverage Schema

至少：

```text
tax_case_id
evidence_coverage
total_evidence_coverage_loss
evidence_loss_details[]
```

每条 detail：

```text
evidence_requirement_instance_id
evidence_requirement_id
evidence_state_id
state
configured_loss
state_factor
actual_evidence_coverage_loss
```

状态系数：

```text
provided = 0
unknown = 0.5
missing = 1
not_applicable = 不评分
未来无 State = 不评分
```

---

# 一百零三、统一 Root Schema 与版本

正式采用：

```text
模块化子 Schema
+
agent_schema.json Root Schema
```

Root 只代表：

```text
全部核心模块已经完成后的当前完整 Tax Case 最终快照
```

中间 Workflow 不要求 Root Schema 合法；各节点使用各自模块 Schema。

Root 不保存 execution history；历史运行结果进入 execution log / audit history。

只有 Root 保存：

```text
schema_version
```

各顶层模块运行输出不重复保存 `schema_version`，但 Git 中的 Schema / Prompt / Rule / Registry 文件本身仍必须版本管理。

Root 至少组合：

```text
schema_version
tax_case
contract_facts
actual_facts
economic_substance
evidence
transaction_facts
consistency_check
regulation_results
rule_engine_input
rule_engine_output
tax_judgement
tax_impact_results
risk_events
tax_health_score
evidence_coverage
next_actions
final_report
```

所有子模块 `tax_case_id` 必须一致。

`rule_engine_input` 即使可由其他对象重构，也保留在最终 Root 中，用于审计“本次 Rule Engine 实际读取了哪些对象”。

---

# 一百零四、统一 Registry 管理

所有跨模块稳定值统一 Registry 管理。

至少包括：

```text
Economic Substance Registry
Tax Type Registry
Invoice Type Registry
Evidence Requirement Registry
Risk Event Registry
Tax Treatment Item Registry
Contract Fact Relation Type Registry
Actual Fact Relation Type Registry
Scope Type Registry
Risk Trigger Rule Registry
Scoring Profile Registry
Payment Nature Registry
Payment Method Registry
Trigger Event Registry
Rule Status Registry / Enum
Evidence State Enum
Consistency Status Enum
Risk Level Enum
Working Day Calendar Registry
```

Registry 采用项目当前最新版本，不对 Tax Case 做 registry version pin。

旧 Case 重跑使用当前最新 Registry。

---

# 一百零五、统一严格单向流转

正式链路必须严格保持：

```text
Tax Case / Files
↓
Contract Facts / Actual Facts / Actual Tax Treatments / Actual Obligation States
↓
Economic Substance / Evidence / Relations
↓
Transaction Facts / Consistency
↓
Temporal RAG / Regulation Result
↓
Rule Engine
↓
Judgement Resolution
↓
Tax Judgement / Tax Impact
↓
Risk Trigger / Risk Events / Scores
↓
Next Actions / Final Report
```

任何下游模块不得直接修改上游对象。

发现上游问题时只能：

```text
输出 unknown
输出 needs_review
输出 conflict
或触发对应上游节点重跑
```

不得为了得到确定结论而在下游补造事实。

---

# 一百零六、v0.6 执行优先事项

v0.6 之后正式实施顺序：

```text
1. 将 v0.6 同步进入 Git，作为当前最高规范
2. 以 JSON Schema v1.1 作为后续正式接口版本
3. 冻结 Economic Substance / Evidence Requirement / Tax Treatment Item / Risk Event Registries
4. 冻结 Risk Trigger Rules 与 Scoring Profile / Mapping Tables
5. 成员 C 按 Schema v1.1 编码 Rule Engine、Risk Trigger、评分与接口校验
6. 业务成员提供 Golden Test 的业务 expected，不负责测试框架实现
7. 成员 C 负责 Golden Test 自动化、Schema 校验、Dify / Rule Engine 联调
8. 完成 Registry / Rule Table 后进入 Dify Workflow 正式接线
```

后续只对会明显改变整个 Agent 架构、Tax Judgement、Rule Engine、评分体系或核心 Schema 走向的问题继续征求人工选择；普通字段、局部引用和低影响实现细节直接按本统一原则落地。

---

# 一百零七、统一 Actual Tax Treatment

正式新增：

```text
actual_tax_treatments[]
```

用途：

```text
记录企业在申报表、税务处理记录或其他正式税务材料中“实际采用了什么税务处理”
```

最小粒度：

```text
一个 actual_tax_treatment
→ 一个 tax_type
→ 一个 treatment_item
→ 一个实际 value
```

基础结构：

```json
{
  "actual_tax_treatment_id": "actual_tax_treatment_001",
  "tax_type": "vat",
  "treatment_item": "tax_rate",
  "value": 0.03,
  "tax_period_start": "2026-07-01",
  "tax_period_end": "2026-07-31",
  "sources": []
}
```

同一申报材料可形成多个原子 Actual Tax Treatment。

Actual Tax Treatment 仍然遵守：

```text
只提取材料直接支持的值
不从其他金额反算税率
不从 Tax Judgement 回填实际处理
不从法规推断企业实际采用的处理
```

如对象存在但 `value` 本身存在可靠冲突或无法确定：

```text
value = null
+
actual_fact_issues[]
```

Risk Trigger 仅使用不存在 blocking issue 且 value 已确认的 Actual Tax Treatment。

---

# 一百零八、统一 Tax Treatment Item Registry

`actual_tax_treatments[].treatment_item` 必须来自固定 Registry。

第一版至少包括：

```text
applicability
taxpayer
taxable_activity
income_type
tax_base_amount
tax_rate
levy_rate
declared_tax_amount
preference_type
preference_applied
preference_rate
withholding_agent
withholding_basis
withholding_rate
withheld_tax_amount
tax_liability_date
income_recognition_period
withholding_date
```

发票自身的：

```text
invoice_type
invoice_item
invoice_amount
invoice_date
```

继续由 `actual_invoices[]` 保存，不在 Actual Tax Treatment 中重复。

---

# 一百零九、统一 Actual Obligation State

正式新增：

```text
actual_obligation_states[]
```

只用于保存能够被材料正面确认的实际义务履行状态。

基础状态：

```text
confirmed_done
confirmed_not_done
```

适用的 `obligation_type` 至少包括：

```text
tax_filing
tax_payment
withholding
invoice_issuance
```

核心禁止：

```text
未上传材料
数组为空
Evidence missing
Evidence unknown
```

均不得推出：

```text
confirmed_not_done
```

因此：

```text
absence ≠ not done
```

继续作为全局事实原则。

---

# 一百一十、统一 Actual Fact Relation 扩展

`actual_fact_relations[]` 继续只连接：

```text
Actual Fact ↔ Contract Fact
```

但 `relation_type` 不再硬编码为单一 `actual_execution_of`，统一由：

```text
Actual Fact Relation Type Registry
```

管理。

第一版至少允许：

```text
actual_execution_of
actual_tax_treatment_of
actual_obligation_state_of
```

若 Actual Tax Treatment / Actual Obligation State 只能确认到：

```text
Case + tax_type + tax_period
```

则允许没有 Contract Fact relation，不得强行映射具体合同阶段或 Transaction Fact。

---

# 一百一十一、统一 Transaction Fact 对税务实际处理的承载

如果 Actual Tax Treatment / Actual Obligation State 能够可靠归属于某个具体业务链：

```text
→ 允许进入该 Transaction Fact 的 actual_fact_refs[]
```

如果只能确认到 Case / tax_type / tax_period：

```text
→ 保持 Case 级 Actual Fact
→ 不强行放入 Transaction Fact
```

Transaction Fact 仍然只是引用组合视图，不复制 Actual Tax Treatment 的值。

---

# 一百一十二、统一 Risk Trigger 五类固定模式

Risk Trigger 优先由固定模式构造，不为每种风险编写完全不同的自由逻辑。

## Pattern 1：expected / actual mismatch

```text
resolved expected value
≠
confirmed actual value
→ incorrect_*
```

适用于：

```text
taxable_activity
income_type
tax_base
tax_rate
levy_rate
preference
withholding_basis
withholding_rate
```

## Pattern 2：amount difference

```text
expected_tax_amount > actual_tax_amount
→ underpayment / underwithheld

expected_tax_amount < actual_tax_amount
→ overpayment
```

## Pattern 3：deadline comparison

```text
actual_date > resolved_deadline
→ late_*
```

## Pattern 4：obligation not performed

```text
resolved obligation = true
+
actual_obligation_state = confirmed_not_done
→ *_not_performed
```

## Pattern 5：incorrect preference application

```text
resolved eligibility = false
+
actual preference_applied = true
→ incorrect_preference_application
```

---

# 一百一十三、统一 Risk Trigger Guard

Formal Risk Event 只允许在以下 Guard 全部满足后生成：

```text
expected resolution = resolved
actual comparison fact 已确认
scope / tax_type / tax_period 可可靠对应
不存在影响本次比较的 conflict / duplicate / needs_review
金额比较币种一致，或已有合法确定性转换结果
```

任一 Guard 不满足：

```text
Risk Trigger = not_evaluable
```

`not_evaluable` 只属于 Risk Trigger Engine 内部运行状态：

```text
不生成 Formal Risk Event
不进入 Tax Health Score
不自动变成 Evidence Risk
```

Risk Trigger 自己不得查汇率、重新解释合同或法规、重新做 Tax Judgement。

---

# 一百一十四、统一 Risk Event Registry 第一版分类

Risk Event Registry 采用：

```text
risk_event_type
risk_event_name
risk_family
tax_type
target_judgement_items[]
scoring_profile_id
version
```

核心风险族至少包括：

```text
tax_scope
tax_calculation
tax_payment
filing
payment
income_tax
individual_tax
withholding
invoice
tax_timing
preference
```

正式 Risk Event 只来自固定 Risk Trigger Rule。

以下事项不得进入 Formal Risk Event：

```text
missing_evidence
unknown_evidence
low_evidence_coverage
contract_fact_conflict
actual_fact_conflict
possible_duplicate
consistency_needs_review
economic_substance_uncertain
provisional_tax_judgement
unknown_tax_judgement
```

这些事项进入：

```text
Final Report.pending_items
Final Report.unknown_items
Final Report.evidence_gaps
```

---

# 一百一十五、统一 Scoring Profile

Risk Event Registry 不保存五个动态死分值，只指定：

```text
scoring_profile_id
```

Scoring Profile 固定决定相对稳定的：

```text
tax_consequence_severity
obligation_violation_severity
```

第一版：

```text
tax_treatment_error
→ consequence = 2
→ obligation = 1

tax_shortfall
→ consequence = 2
→ obligation = 2

tax_overpayment
→ consequence = 1
→ obligation = 1

late_obligation
→ consequence = 2
→ obligation = 2

obligation_not_performed
→ consequence = 3
→ obligation = 4

invoice_missing
→ consequence = 2
→ obligation = 3

invoice_content_error
→ consequence = 1
→ obligation = 1

tax_timing_error
→ consequence = 1
→ obligation = 1
```

如果已经有结构化证据确认处罚、强制执行等更严重法律后果，允许固定 Mapping 升级 consequence，但 LLM 不得自由升级。

---

# 一百一十六、统一 Tax Amount Impact Mapping

`tax_amount_impact` 只使用确定性 Tax Impact Result。

如果：

```text
tax_difference_amount = null
```

则：

```text
tax_amount_impact = 0
```

绝对金额映射：

```text
0                        → 0
>0 – 10,000             → 1
>10,000 – 50,000        → 2
>50,000 – 200,000       → 3
>200,000                 → 4
```

相对金额：

```text
abs(tax_difference_amount)
÷
相关交易确定金额
```

映射：

```text
0                        → 0
>0 – 1%                  → 1
>1% – 3%                 → 2
>3% – 10%                → 3
>10%                      → 4
```

能够同时计算绝对与相对金额时：

```text
取两者较高分
```

交易金额无法可靠取得时：

```text
仅使用绝对金额
```

同一 `impact_group_id` 的底层税差只允许计算一次金额影响，优先分配给：

```text
underpayment
underwithheld
overpayment
```

等结果型 Risk Event。

---

# 一百一十七、统一 Duration Severity Mapping

已确认持续时间：

```text
无法确认 / 无持续性质                  → 0
≤30 天，或 1 个期间                  → 1
31–90 天，或 2–3 个连续期间          → 2
91–365 天，或 4–12 个连续期间        → 3
>365 天，或超过 12 个连续期间        → 4
```

若同时可确定天数与期间数：

```text
取较高等级
```

不得因为“可能持续很久”而估算。

---

# 一百一十八、统一 Impact Scope Mapping

影响范围以已确认独立交易范围为基础：

```text
无法确认                                  → 0
1 个独立交易范围                          → 1
2–3 个独立交易范围                        → 2
4–10 个独立交易范围                       → 3
>10 个独立交易范围 / 已确认 Case 级系统性影响 → 4
```

主要依据：

```text
related_transaction_fact_ids[]
substance_codes[]
```

不得仅因为合同复杂而提高影响范围。

---

# 一百一十九、统一 Risk Suppression 后评分

完整链路统一为：

```text
Formal Risk Events
↓
Risk Merge
↓
Consequence Suppression
↓
impact_group monetary dedup
↓
Scorable Risk Events
↓
Tax Health Score
```

因此：

```text
Formal Risk Event
≠ 必然单独扣分
```

当上游原因风险的全部已确认后果已经被更具体的最终 Risk Event 完整表达时：

```text
→ 上游 Risk Event 保留审计链
→ 不再重复进入 Health Score
```

若下游仍存在 provisional / unknown：

```text
→ 不得提前 suppression 上游风险
```

---

# 一百二十、统一 Golden Test 分工边界

Golden Test 属于共同验收机制，但职责分开：

业务成员负责：

```text
提供业务 Case
确认 Contract Facts / Economic Substance / Tax Judgement / Risk / Score expected
确认关键业务断言
```

成员 C 负责：

```text
测试代码
自动化比较
Schema validator
Golden Test runner
Dify / Rule Engine 联调
失败定位与接口修复
```

业务成员无需维护自动化测试框架。

