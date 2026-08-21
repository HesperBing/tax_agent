# Dify Workflow 技术规划 v0.6

## 一、文件说明

本文档用于规划Tax Agent各模块在Dify中的连接方式、输入输出和执行顺序。

当前状态：

- 版本：v0.6
- 类型：技术草图
- 暂不进行正式接线
- 等待Schema、Registry、Risk Trigger Rules和Scoring Mapping Tables冻结后再正式实现

Dify只负责工作流编排和数据传递，不能擅自修改统一原则、业务规则或正式Schema。

## 二、工作流目标

用户创建一个Tax Case并上传合同及相关材料后，系统完成：

1. 文件分类
2. 合同事实提取
3. 实际事实提取
4. 经济实质识别
5. 证据状态分析
6. 交易事实组装
7. 合同与实际履约一致性检查
8. 有效税务法规检索
9. 确定性规则判断
10. 风险识别与评分
11. 生成下一步行动
12. 生成最终税务健康报告

当前版本不设置补充问答节点，也不接受用户自然语言描述作为正式事实来源。

## 三、工作流输入

Workflow输入至少包括：

- tax_case_id
- source_files
- file_content
- file_metadata
- workflow_version

只有成功完成文件分类的文件，才能进入正式`source_files[]`并支持后续事实提取。

## 四、工作流输出

最终输出至少包括：

- tax_case
- contract_facts
- actual_facts
- economic_substance
- evidence
- transaction_facts
- consistency_check
- regulation_results
- rule_engine_input
- rule_engine_output
- tax_judgement
- tax_impact_results
- risk_events
- tax_health_score
- evidence_coverage
- next_actions
- final_report

全部模块完成后，由`agent_schema.json`组成完整Tax Case最终快照。

## 五、Dify节点规划

| 节点 | 节点名称 | 主要职责 | 主要输出 |
|---|---|---|---|
| N01 | Start | 接收Tax Case和上传文件 | 原始输入 |
| N02 | File Classification | 识别文件类型和合同文件角色 | source_files |
| N03 | Contract Facts Extraction | 从合同中提取合同事实 | contract_facts |
| N04 | Contract Relations | 生成合同事实之间的关系 | contract_fact_relations |
| N05 | Economic Substance | 仅根据Contract Facts识别经济实质 | economic_substance |
| N06 | Actual Facts Extraction | 从实际材料中提取实际事件 | actual_facts |
| N07 | Actual Tax Treatment | 提取实际采用的税务处理 | actual_tax_treatments |
| N08 | Actual Obligation State | 提取有材料证明的义务履行状态 | actual_obligation_states |
| N09 | Actual Relations and Issues | 生成关系、冲突和重复事件信息 | relations、issues、duplicate_groups |
| N10 | Evidence Processing | 生成证据要求实例和证据状态 | evidence |
| N11 | Transaction Facts Assembly | 组合上游对象引用 | transaction_facts |
| N12 | Consistency Check | 比较Contract Facts与Actual Facts | consistency_check |
| N13 | Temporal RAG | 按交易适用时间检索法规 | 法规检索结果 |
| N14 | Regulation Result | 将法规结果转换为标准结构 | regulation_results |
| N15 | Rule Engine Input Assembly | 组装规则引擎输入引用 | rule_engine_input |
| N16 | Schema Validation | 校验Rule Engine输入 | validation_result |
| N17 | Atomic Rule Engine | 执行确定性规则 | rule_execution_results |
| N18 | Judgement Resolution | 聚合同一判断项目的规则结果 | judgement_resolution_results |
| N19 | Tax Judgement | 根据Resolution形成税务判断 | tax_judgement |
| N20 | Tax Impact | 计算税额和税务影响 | tax_impact_results |
| N21 | Risk Trigger | 执行固定风险触发模式 | risk_trigger_results |
| N22 | Risk Event Processing | 生成、合并和抑制风险事件 | risk_events |
| N23 | Scoring | 计算两项独立评分 | tax_health_score、evidence_coverage |
| N24 | Next Actions | 根据正式风险生成处理建议 | next_actions |
| N25 | Final Report | 根据结构化结果生成报告 | final_report |
| N26 | Root Validation | 使用agent_schema.json校验完整结果 | 完整Case快照 |
| N27 | End | 返回最终结果 | Workflow输出 |

## 六、严格执行顺序

正式工作流必须保持以下单向流程：

Tax Case和文件

→ Contract Facts、Actual Facts、Actual Tax Treatments、Actual Obligation States

→ Economic Substance、Evidence和Relations

→ Transaction Facts和Consistency Check

→ Temporal RAG和Regulation Result

→ Rule Engine Input和Atomic Rules

→ Judgement Resolution

→ Tax Judgement和Tax Impact

→ Risk Trigger和Risk Events

→ Tax Health Score和Evidence Coverage

→ Next Actions和Final Report

禁止出现：

`Tax Judgement → Rule Engine → Tax Judgement`

下游节点不得直接修改上游节点已经形成的正式对象。

## 七、大模型节点

DeepSeek主要用于：

- Contract Facts Extraction
- Actual Facts Extraction
- Economic Substance
- 受控语义判断
- Final Report

大模型节点必须输出结构化JSON，并通过对应Schema校验。

大模型不能：

- 创建材料中不存在的事实
- 将unknown改成确定状态
- 根据缺少材料认定某项义务没有完成
- 自由生成Risk Event
- 自由决定评分
- 修改规则引擎结果

正式Prompt必须同步保存在Git的`prompts/`目录中，不能只保存在Dify节点内。

## 八、Rule Engine连接方式

Rule Engine由Python实现，Dify通过HTTP请求节点或后端接口调用。

Dify向Rule Engine传入：

- tax_case_id
- transaction_fact_refs
- economic_substance_refs
- consistency_check_refs
- regulation_result_refs
- evidence_state_refs
- actual_tax_filing_refs
- actual_tax_payment_refs

Rule Engine返回：

- rule_execution_results
- judgement_resolution_results
- tax_impact_results
- risk_trigger_results
- risk_events
- tax_health_score
- evidence_coverage

具体接口字段以JSON Schema v1.1为准。

## 九、异常和分支处理

### 文件分类失败

文件分类失败时：

- 该文件不进入正式source_files
- 记录文件处理技术错误
- 单个非关键文件失败不阻断整个Tax Case
- 剩余有效文件继续处理

### Schema校验失败

Schema校验失败时：

- 停止当前模块向下传递错误数据
- 返回统一错误结构
- 记录failed_stage
- 修复后重新执行对应模块

### 业务信息不足

出现以下情况时，Workflow仍可继续：

- unknown
- partial
- needs_review
- conflict
- Evidence missing

这些属于业务状态，不等于技术执行失败。

系统不跳转到补充问答节点，而是在最终结果中生成：

- unknown_items
- pending_items
- evidence_gaps
- next_actions

## 十、统一错误格式

所有技术错误统一返回：

```json
{
  "success": false,
  "error_code": "",
  "error_message": "",
  "failed_stage": ""
}
```

不同Dify节点不得各自设计完全不同的错误结构。

## 十一、环境与密钥

DeepSeek API Key不能直接写入Workflow文件、Prompt或GitHub仓库。

本地测试使用`.env`保存密钥。

Dify中使用平台的模型供应商配置或Secret配置保存密钥。

Git中只保留：

- `.env.example`
- API参数名称
- 模型名称
- 接口地址示例

## 十二、测试计划

正式连接Dify前，需要完成：

1. 各模块Input Schema和Output Schema校验
2. Mock Input和Mock Output测试
3. Rule Engine单元测试
4. Risk Trigger测试
5. 评分边界测试
6. Golden Test Cases自动化
7. DeepSeek API连接测试
8. Dify和Rule Engine接口联调
9. Root Schema完整结果校验

Golden Test只要求结构化关键业务结果一致，不要求最终报告文字逐字一致。

## 十三、正式接线前置条件

以下内容没有确定前，不进入Dify正式接线：

- JSON Schema v1.1
- Economic Substance Registry
- Evidence Requirement Registry
- Tax Treatment Item Registry
- Risk Event Registry
- Actual Fact Relation Type Registry
- Risk Trigger Rules
- Scoring Profile
- Scoring Mapping Tables

完成以上内容后，再按照本文件的节点顺序搭建正式Dify Workflow。

## 十四、版本管理

每个重要Dify Workflow版本都应导出并保存在Git中。

建议文件名：

- workflow_v0_6.yaml
- workflow_v1_0.yaml
- workflow_release_candidate.yaml

不得把唯一可运行版本只保存在Dify平台中。

每次修改节点输入输出、Prompt或执行顺序时，都必须同步更新：

- Schema
- Mock
- Test
- CHANGELOG.md