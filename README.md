# tax_agent

面向中国合同收入场景的税务健康评分与大模型税务助手。

当前统一规范版本：`v0.6`
当前 JSON Schema 版本：`v1.1`

## 项目简介

本项目以一份核心合同关系建立一个Tax Case，将主合同、补充协议、变更协议以及相关的履约、开票、付款和税务材料放在同一个Case中分析。

系统主要检查：

- 合同是怎么约定的
- 交易实际上是怎么履行的
- 税务上应当怎么处理
- 当前材料能够证明到什么程度
- 已确认的税务风险有哪些
- 下一步应该采取什么行动

## 当前业务范围

当前版本主要面向：

- 中国合同收入税务健康评分
- 境内自然人与境内企业
- 服务类及相关合同交易
- 一份核心合同关系对应一个Tax Case

当前版本不设置补充问答模块，也不把用户自然语言描述作为正式事实来源。

事实只能来自成功完成分类并进入`source_files[]`的上传材料。

## 核心处理流程

Tax Case和上传文件

→ Contract Facts、Actual Facts和Economic Substance

→ Evidence和Transaction Facts

→ Consistency Check

→ Temporal RAG和Regulation Result

→ Rule Engine和Judgement Resolution

→ Tax Judgement和Tax Impact

→ Risk Trigger和Risk Events

→ Tax Health Score和Evidence Coverage

→ Next Actions和Final Report

整个流程保持严格单向，不允许形成：

`Tax Judgement → Rule Engine → Tax Judgement`

## 技术组成

- Dify：工作流编排
- DeepSeek：合同理解、事实提取和报告生成
- Temporal RAG：检索交易适用时间内有效的税务法规
- Python Rule Engine：确定性规则、风险和评分计算
- JSON Schema v1.1：模块输入输出校验
- Golden Test Cases：关键业务结果自动化验证

## 项目目录

- `schemas/`：JSON Schema v1.1接口定义与说明
- `enums/`：统一枚举
- `prompts/`：大模型Prompt
- `regulations/`：税务法规资料
- `metadata/`：法规及其他元数据
- `registries/`：跨模块Registry
- `rules/`：税务、风险、证据和一致性规则
- `rule_engine/`：Python规则引擎
- `scoring/`：评分规则与Mapping Tables
- `dify/`：Dify Workflow规划和导出文件
- `mocks/`：模块Mock JSON
- `tests/`：API、Schema和Golden Test
- `docs/`：统一原则和技术架构文档
- `CHANGELOG.md`：项目变更记录

## DeepSeek API

项目使用DeepSeek作为大模型API。

API配置通过本地`.env`文件读取，仓库只提供`.env.example`作为配置模板。

请勿将以下内容上传到GitHub：

- `.env`
- API Key
- `.venv`
- 其他密码或敏感信息

当前已完成DeepSeek API连接测试。

## 当前进度

已经完成：

- GitHub项目仓库
- 基础目录结构
- 统一原则v0.6同步
- 技术架构v0.6
- Dify Workflow v0.6技术规划
- DeepSeek API环境准备和连接测试
- JSON Schema v1.1核心数据结构
- Schema设计决策和最小测试样例
- Schema自动校验，11项测试全部通过

后续工作：

- 冻结各类Registry
- 编写Rule Engine
- 编写Risk Trigger Rules
- 编写评分Mapping Tables
- 准备Mock JSON
- 建立Golden Test自动化
- 完成Dify与Rule Engine联调

## 项目文档

- 当前统一原则：`docs/unified_principles.md`
- 技术架构：`docs/technical_architecture.md`
- Dify规划：`dify/workflow_plan_v0_6.md`
- Schema设计决策：`docs/schema_v1_1_decisions.md`
- Schema文件说明：`schemas/README.md`