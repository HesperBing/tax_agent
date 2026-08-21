# 

# 二、必须统一的数据对象

以下数据对象必须使用统一名称、统一结构、统一字段定义：

1. `Tax Case`

2. `Contract Facts`

3. `Actual Facts`

4. `Evidence State`

5. `Transaction Facts`

6. `Regulation Result`

7. `Tax Judgement`

8. `Consistency Check Result`

9. `Rule Engine Input`

10. `Rule Engine Output`

11. `Tax Impact Result`

12. `Next Actions`

13. `Final Report`

任何模块需要新增字段时，必须先更新统一定义，再修改各自模块。

---

# 三、统一字段命名规则

全项目统一使用：

```Plain Text
snake_case
```

示例：

```Plain Text
contract_date
income_type
withholding_status
evidence_coverage
transaction_stage
```

禁止同一含义出现多套命名。

例如：

```Plain Text
income_type
incomeType
income_category
```

只能保留一种正式字段名。

字段名一旦进入正式版本，原则上不得随意修改。

---

# 四、统一字段类型

每个字段必须明确数据类型。

允许的主要类型：

```Plain Text
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

例如：

```Plain Text
contract_date
```

不能在一个模块中使用日期字符串，在另一个模块中改成时间戳。

---

# 五、统一日期格式

所有业务日期统一使用：

```Plain Text
YYYY-MM-DD
```

例如：

```Plain Text
2026-08-15
```

日期无法确认时统一使用：

```Plain Text
null
```

禁止使用：

```Plain Text
""
"unknown"
"不确定"
"暂无"
```

代替空日期。

---

# 六、统一时间字段含义

以下时间字段必须严格区分：

- `contract_date`

- `transaction_date`

- `payment_date`

- `performance_date`

- `delivery_date`

- `acceptance_date`

- `regulation_valid_from`

- `regulation_valid_to`

任何人不得将不同时间统一压缩为一个 `date` 字段。

同学B 负责确定法规适用时使用哪个时间点。

同学C 负责在 Dify 和代码中实现。

---

# 七、统一金额与币种格式

金额统一使用：

```Plain Text
number
```

币种单独使用：

```Plain Text
currency
```

例如：

```Plain Text
contract_amount
estimated_tax_amount
currency
```

禁止将金额和币种拼接成自由文本。

---

# 八、统一枚举值

所有状态字段必须使用固定枚举。

禁止自由填写自然语言状态。

## 事实状态

统一使用：

```Plain Text
confirmed_done
confirmed_not_done
unknown
pending
not_applicable
```

## 证据状态

统一使用：

```Plain Text
provided
missing
unknown
not_applicable
```

## 一致性状态

统一使用：

```Plain Text
consistent
partial
inconsistent
unknown
needs_review
```

## 风险等级

统一使用：

```Plain Text
low
medium
high
critical
```

## Case 状态

建议统一使用：

```Plain Text
created
facts_extracted
rag_completed
judged
scored
completed
needs_information
error
```

所有枚举值统一维护在：

```Plain Text
/enums
```

目录中。

---

# 九、统一 unknown 处理规则

`unknown` 的统一含义：

> 当前已有事实或证据不足，暂时无法确认。
> 
> 

必须遵守：

- `unknown` 不直接视为违规

- `unknown` 不直接视为已完成

- `unknown` 不直接视为未完成

- 缺少材料时优先影响 Evidence Coverage

- 只有证据足够时，规则引擎才能认定义务已经完成或明确未完成

任何 Prompt、RAG、评分规则和 Python 代码都必须遵守这一规则。

---

# 十、统一 pending 处理规则

`pending` 表示：

> 该事项按照当前交易阶段尚未发生。
> 
> 

例如合同已签但尚未付款时，付款事实可以是 `pending`。

`pending` 与 `unknown` 必须区分。

- `pending`：事情还没有到发生阶段

- `unknown`：事情可能已经发生，但当前无法确认

---

# 十一、统一事实层级

系统必须区分以下三类事实：

## Contract Facts

表示：

```Plain Text
合同写了什么
```

## Actual Facts

表示：

```Plain Text
实际发生了什么
```

## Evidence State

表示：

```Plain Text
当前有什么材料能够证明
```

三类信息不得混用。

统一原则：

- 合同中写明应扣缴，不代表现实中已经扣缴

- 缺少扣缴凭证，不代表已经确认未扣缴

- 合同写明某项服务，不代表实际履约内容完全一致

- 用户口头补充信息需要单独保留来源

---

# 十二、统一 Transaction Facts

`Transaction Facts` 是事实层对后续模块的统一输出。

必须由以下内容汇总形成：

```Plain Text
Contract Facts
+
Actual Facts
+
Evidence State
+
必要的用户补充信息
```

王涵睿 负责业务定义。

王冰 负责技术合并和 Schema 校验。

---

# 十三、统一文件分类

上传文件必须使用固定文件类型。

建议统一：

```Plain Text
contract
invoice
payment_receipt
withholding_certificate
tax_payment_certificate
acceptance_material
delivery_material
other
unknown
```

王涵睿 负责文件分类业务规则。

王冰 负责文件识别技术实现。

---

# 十四、统一文件来源记录

每一条关键事实都应尽量保留来源。

建议统一记录：

```Plain Text
source_file_id
source_file_type
source_page
source_text
extraction_confidence
```

这样后续出现错误时，可以追溯事实来源。

---

# 十五、统一置信度范围

所有模型置信度统一使用：

```Plain Text
0.00 - 1.00
```

例如：

```Plain Text
income_type_confidence
contract_facts_confidence
```

禁止有的模块使用百分比，有的模块使用小数。

---

# 十六、统一 Temporal RAG 输入

Temporal RAG 必须接收结构化检索条件。

至少统一包含：

- `applicable_date`

- `business_type`

- `subject_type`

- `economic_substance`

- `tax_type`

- `transaction_stage`

根据实际场景可增加：

- `contract_date`

- `transaction_date`

- `payment_date`

- `performance_date`

禁止只把整份合同全文直接交给知识库检索。

---

# 十七、统一法规 Metadata

法规库至少统一以下 Metadata：

- `law_id`

- `title`

- `document_no`

- `issuer`

- `tax_type`

- `business_type`

- `subject_type`

- `valid_from`

- `valid_to`

- `article`

- `source`

- `version_status`

字段名一旦冻结，不得随意修改。

同学B 负责业务定义和法规内容。

同学C 负责知识库字段配置。

---

# 十八、统一法规时间规则

每条法规必须明确：

```Plain Text
valid_from
valid_to
```

如果仍然有效：

```Plain Text
valid_to = null
```

或采用项目统一的长期有效表示方式。

三人必须统一使用同一种方案。

禁止一部分法规使用 `null`，另一部分使用 `9999-12-31`。

---

# 十九、统一 Regulation Result

Temporal RAG 输出必须结构化。

每条法规结果至少包含：

- `law_id`

- `title`

- `document_no`

- `article`

- `valid_from`

- `valid_to`

- `source`

- `applicable_reason`

- `retrieval_score`

Regulation Result 禁止只有一段无法追踪来源的自然语言说明。

---

# 二十、统一 Tax Judgement

Tax Judgement 是规则引擎读取的标准化税务判断。

必须统一字段、枚举和值域。

至少应覆盖项目需要的：

- 所得类型

- 所得类型置信度

- 扣缴义务

- 扣缴状态

- 发票义务

- 发票状态

- 增值税适用状态

- 税费承担条款状态

- 交易阶段

- 付款状态

- 合同与实际服务一致性

- 关键证据状态

Tax Judgement 不得直接输出最终 Health Score。

---

# 二十一、统一 Consistency Check

Consistency Check 专门检查：

```Plain Text
合同约定
↕
实际履约
↕
法定税务义务
```

输出状态统一使用：

```Plain Text
consistent
partial
inconsistent
unknown
needs_review
```

Consistency Check 本身不直接修改分数。

评分由 Rule Engine 根据同学A 的规则决定。

---

# 二十二、统一评分规则格式

同学A 设计的每一条评分规则必须采用固定结构。

至少包含：

- `rule_id`

- `rule_name`

- `trigger_condition`

- `health_score_loss`

- `evidence_coverage_loss`

- `risk_level`

- `reason`

- `applicable_scope`

- `required_fields`

- `unknown_handling`

- `version`

禁止使用口头描述作为正式规则。

---

# 二十三、统一 Rule ID

每条规则必须有唯一 `rule_id`。

例如项目内部可以采用统一格式：

```Plain Text
RISK_001
RISK_002
EVIDENCE_001
CONSISTENCY_001
```

具体命名方案由三人一次性确认。

正式使用后：

- 不重复

- 不随意改名

- 不删除后复用旧编号

同学B 维护规则清单。

同学C 的 Python Rule Engine 与 Rule ID 一一对应。

---

# 二十四、统一评分顺序

Rule Engine 的处理顺序必须固定。

建议统一为：

```Plain Text
1. 输入校验
2. 判断适用规则
3. 判断 confirmed / unknown / pending
4. 计算已确认风险
5. 计算 Health Score
6. 计算 Evidence Coverage
7. 计算 Risk Level
8. 输出 Risk Codes
9. 输出 Evidence Gaps
10. 输出 Next Actions 所需状态
```

所有版本使用同一基本顺序。

---

# 二十五、统一 Health Score 原则

Tax Health Score 只反映：

```Plain Text
当前已确认事实下的税务风险
```

禁止因为单纯缺少材料直接进行等额风险扣分。

评分规则由同学A 统一维护。

代码实现由同学C 负责。

---

# 二十六、统一 Evidence Coverage 原则

Evidence Coverage 只反映：

```Plain Text
当前结论有多少证据支撑
```

同学A 负责定义不同证据缺口如何影响 Evidence Coverage。

同学C 负责计算实现。

---

# 二十七、统一风险等级

Risk Level 必须由统一规则产生。

禁止：

- A 自己判断 medium

- C 代码判断 high

- Final Report 又让 LLM 改成 low

Risk Level 必须以 Rule Engine 输出为最终结果。

---

# 二十八、统一 LLM 权限边界

LLM 可以负责：

- 文件内容理解

- 合同经济实质识别

- 实际履约事实提取

- 标准化 Tax Judgement

- 最终结果解释

LLM 不允许：

- 自由修改 Health Score

- 自由修改 Evidence Coverage

- 自由改变 Risk Level

- 自行新增评分规则

- 自行改写法规有效期

---

# 二十九、统一 RAG 权限边界

Temporal RAG 负责：

- 提供与交易时间匹配的法规

- 提供法规条款

- 提供法规来源

- 提供法规适用依据

RAG 不负责：

- 直接扣分

- 直接计算 Health Score

- 修改 Evidence Coverage

- 自行决定最终风险等级

---

# 三十、统一 Rule Engine 权限边界

Rule Engine 负责：

- 确定性判断

- 风险识别

- Health Score

- Evidence Coverage

- Risk Level

- Risk Codes

- Evidence Gaps

Rule Engine 不负责：

- 自己创造新的税法判断

- 自己修改法规内容

- 自己猜测缺失事实

---

# 三十一、统一 Final Report 规则

Final Report 必须读取上游已经确定的数据。

最终报告至少包含：

- 合同基本情况

- 收入性质判断

- 实际履约情况

- 一致性结论

- 主要税务风险

- 扣分原因

- Evidence Coverage

- 法规依据

- 当前无法确认事项

- 税务影响

- 整改建议

- 下一步行动

Final Report 不得重新计算或修改：

```Plain Text
Tax Health Score
Evidence Coverage
Risk Level
Risk Codes
```

---

# 三十二、统一模块输入输出规则

每个模块必须明确四件事：

```Plain Text
输入是什么
输出是什么
缺字段怎么办
出错怎么办
```

每个模块都要有：

- Input Schema

- Output Schema

- Error Handling

- Mock Input

- Mock Output

---

# 三十三、统一错误返回格式

技术错误建议统一为：

```Plain Text
{
  "success": false,
  "error_code": "",
  "error_message": "",
  "failed_stage": ""
}
```

禁止不同节点各自输出不同格式的错误。

---

# 三十四、统一 Mock JSON

必须准备以下 Mock：

- `tax_case_mock.json`

- `contract_facts_mock.json`

- `actual_facts_mock.json`

- `evidence_state_mock.json`

- `transaction_facts_mock.json`

- `regulation_result_mock.json`

- `tax_judgement_mock.json`

- `consistency_check_mock.json`

- `rule_engine_output_mock.json`

作用：

- 上游模块未完成时，下游仍能开发

- 提前测试接口

- 提前发现字段冲突

- 避免三个人互相等待

---

# 三十五、统一 Golden Test Cases

三人必须共用一套 Golden Test Cases。

每个案例至少保存：

- 输入文件

- 预期 Contract Facts

- 预期 Actual Facts

- 预期 Evidence State

- 预期 Regulation Result

- 预期 Tax Judgement

- 预期 Consistency Check

- 预期 Risk Codes

- 预期 Health Score

- 预期 Evidence Coverage

- 预期报告重点

同学A 负责事实、Tax Judgement 和评分预期。

同学B 负责法规、RAG 和 Consistency Check 预期。

同学C 负责自动执行和结果对比。

---

# 三十六、统一版本号

以下资产必须有版本：

- Schema

- Enums

- Prompt

- Regulations Metadata

- Temporal RAG Rules

- Tax Judgement

- Consistency Check Rules

- Scoring Rules

- Rule Engine

- Dify Workflow

- Golden Test Cases

建议版本形式：

```Plain Text
v0.1
v0.2
v1.0
```

---

# 三十七、统一 Change Log

项目统一维护：

```Plain Text
CHANGELOG.md
```

每次关键修改必须记录：

- 修改日期

- 修改人

- 修改内容

- 修改原因

- 影响模块

- 是否需要重新测试

---

# 三十八、统一 Git 目录

建议统一目录：

```Plain Text
tax-agent/
├── schemas/
├── enums/
├── prompts/
├── regulations/
├── metadata/
├── rules/
├── rule_engine/
├── dify/
├── mocks/
├── tests/
├── docs/
└── CHANGELOG.md
```

责任建议：

```Plain Text
schemas/        C维护技术规范，A/B确认业务
enums/          A定义业务含义，C固化
prompts/        A为主
regulations/    B为主
metadata/       B为主
rules/          A为主
rule_engine/    C为主
dify/           C为主
mocks/          三人共同维护
tests/          三人共同维护
docs/           三人共同维护
CHANGELOG.md    C维护，所有人提交变更
```

---

# 三十九、统一文件命名

文件命名统一使用：

```Plain Text
lower_snake_case
```

例如：

```Plain Text
contract_facts_schema.json
tax_judgement_schema.json
scoring_rules_v1.md
regulations_metadata.csv
workflow_v1.yaml
```

禁止随意出现：

```Plain Text
最终版
最终版2
最终版真的
new
new2
latest
latest_final
```

---

# 四十、统一 Prompt 管理

Prompt 不得只保存在 Dify 节点中。

必须同步保存到 Git。

每个 Prompt 至少记录：

- Prompt 名称

- 对应模块

- 输入字段

- 输出字段

- 当前版本

- 修改时间

- 修改人

---

# 四十一、统一 Dify Workflow 管理

Dify 中的重要 Workflow 每到关键版本应导出保存。

建议至少保存：

```Plain Text
workflow_v0.5
workflow_v1.0
workflow_release_candidate
workflow_final
```

不得把唯一可运行版本只留在 Dify Cloud 中。

---

# 四十二、统一接口变更流程

以下内容发生变化时，必须走变更流程：

- 字段名

- 字段类型

- 枚举值

- JSON 层级

- Rule ID

- 法规 Metadata

- Workflow 输入输出

- Prompt 输出格式

- Rule Engine 输出格式

变更流程统一为：

```Plain Text
提出修改
↓
说明原因
↓
确认影响模块
↓
三人确认
↓
修改正式文件
↓
修改上下游
↓
更新 Mock
↓
重新测试
↓
更新 CHANGELOG
```

---

# 四十三、统一接口冻结时间

项目进入最终联调阶段后，设置 Interface Freeze。

Freeze 后原则上禁止修改：

- 字段名称

- 字段类型

- 枚举值

- JSON 结构

- Rule ID

- Metadata 字段

- 模块输入输出

确有必要修改时，必须三人共同确认。

