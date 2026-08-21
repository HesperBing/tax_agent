# Schema文件说明

| 文件 | 作用 |
|---|---|
| `common_defs_schema.json` | 公共日期、金额、状态、来源和Judgement Atom定义 |
| `tax_case_schema.json` | Tax Case元数据、模块状态和文件分类结果 |
| `contract_facts_schema.json` | 合同事实、term/stage、关系和冲突 |
| `actual_facts_schema.json` | 实际履约、开票、付款、申报、缴税和实际税务处理 |
| `economic_substance_schema.json` | 经济实质Component |
| `evidence_schema.json` | Evidence Requirement Instance和Evidence State |
| `transaction_facts_schema.json` | 上游事实引用组合视图 |
| `consistency_check_schema.json` | Contract Facts与Actual Facts比较结果 |
| `regulation_result_schema.json` | Temporal RAG结构化法规结果 |
| `rule_schema.json` | Atomic Rule、Evidence Group和Risk Trigger Rule配置 |
| `rule_engine_input_schema.json` | Rule Engine引用型输入 |
| `rule_engine_output_schema.json` | Rule Execution与Judgement Resolution |
| `tax_judgement_schema.json` | 九个预定义税务判断模块 |
| `tax_impact_result_schema.json` | 确定性税务金额影响 |
| `risk_event_schema.json` | Formal Risk Event与五维严重度 |
| `scoring_schema.json` | Tax Health Score和Evidence Coverage |
| `next_actions_schema.json` | 正式风险对应的整改行动 |
| `final_report_schema.json` | 最终报告结构 |
| `agent_schema.json` | 全部模块完成后的Root最终快照 |

正式入口为`agent_schema.json`。`README.md`不是JSON Schema文件，不参与校验。
