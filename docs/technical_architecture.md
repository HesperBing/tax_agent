# Tax Agent 技术架构 v0.6

## 一、项目目标

本项目面向中国合同收入场景，建设合同税务健康评分与大模型税务助手。

系统以一份核心合同关系建立一个 Tax Case，将主合同、补充协议、变更协议以及相关的履约、开票、付款和税务材料统一分析。

系统主要输出：

- Contract Facts
- Actual Facts
- Economic Substance
- Tax Judgement
- Tax Impact
- Risk Events
- Tax Health Score
- Evidence Coverage
- Next Actions
- Final Report

当前版本不设置补充问答模块，也不把用户自然语言描述作为正式事实来源。

## 二、主要技术组成

### 1. Dify Workflow

Dify负责连接各个处理节点、传递模块数据和控制整体执行顺序。

Dify不负责自由修改业务规则，也不能绕过Schema直接改变正式数据结构。

### 2. DeepSeek大模型

DeepSeek主要负责：

- 识别文件内容
- 提取合同事实
- 提取实际履约事实
- 识别合同经济实质
- 进行受控语义判断
- 根据结构化结果生成最终报告

DeepSeek不能：

- 创造材料中不存在的事实
- 把unknown强行改成确定事实
- 自由决定最终评分
- 修改规则引擎已经产生的结果

### 3. Temporal RAG

Temporal RAG负责根据交易适用时间检索当时有效的税务法规。

检索结果形成结构化Regulation Result，供Rule Engine使用。

### 4. Python Rule Engine

Rule Engine负责确定性处理，包括：

- Atomic Rule执行
- Judgement Resolution
- 税务判断收敛
- 税额和税务影响计算
- Risk Trigger执行
- Risk Event生成与合并
- Tax Health Score计算
- Evidence Coverage计算

### 5. JSON Schema v1.1

所有核心模块使用JSON Schema v1.1校验输入和输出。

Root Schema使用：

`schemas/agent_schema.json`

各模块使用独立子Schema，Root Schema只负责引用和组合，不重复定义各模块字段。

## 三、严格单向工作流

系统正式处理顺序如下：

1. 用户创建Tax Case
2. 上传合同及相关交易材料
3. 文件分类和合同文件角色识别
4. 提取Contract Facts和Contract Fact Relations
5. 根据Contract Facts识别Economic Substance
6. 提取Actual Facts、Actual Tax Treatments和Actual Obligation States
7. 生成Actual Fact Relations、Issues和Duplicate Groups
8. 生成Evidence Requirement Instances和Evidence States
9. 组装Transaction Facts
10. 执行Consistency Check
11. Temporal RAG检索有效法规
12. 形成Regulation Result
13. 组装Rule Engine Input
14. 执行Atomic Rules
15. 生成Judgement Resolution Results
16. 形成Tax Judgement
17. 计算Tax Impact Result
18. 执行Risk Trigger Rules
19. 生成、合并和抑制Risk Events
20. 计算Tax Health Score
21. 计算Evidence Coverage
22. 生成Next Actions
23. 生成Final Report
24. 通过agent_schema.json组装完整Case快照

禁止形成以下循环：

`Tax Judgement → Rule Engine → Tax Judgement`

任何下游模块都不能直接修改上游模块的数据。

## 四、模块数据关系

### 1. 文件与Tax Case

只有成功完成文件分类并进入`source_files[]`的文件，才能作为正式事实来源。

文件分类失败时：

- 该文件不能支持Contract Facts
- 该文件不能支持Actual Facts
- 该文件不能支持Evidence State
- 单个非关键文件失败不一定导致整个Tax Case失败

### 2. Contract Facts

Contract Facts只记录合同材料明确约定的内容。

主合同、补充协议和变更协议合并形成当前有效的Contract Facts。

合同对象之间的关系统一存入：

`contract_fact_relations[]`

### 3. Actual Facts

Actual Facts只记录已上传材料能够直接证明的实际事件。

正式Actual Fact对象存在，表示材料中观察到了该事件。

Actual Fact对象不存在，不代表已经确认该事项没有完成。

实际税务处理存入：

`actual_tax_treatments[]`

实际义务履行状态存入：

`actual_obligation_states[]`

### 4. Evidence

证据要求来自固定的Evidence Requirement Registry。

系统依次形成：

- Evidence Requirement
- Evidence Requirement Instance
- Evidence State

证据状态包括：

- provided
- missing
- unknown
- not_applicable

缺少材料优先影响Evidence Coverage，不直接认定为税务违规。

### 5. Transaction Facts

Transaction Facts是上游对象的引用组合视图。

它引用Contract Facts、Actual Facts和Evidence State，但不重复复制金额、日期和税率等数据。

### 6. Consistency Check

Consistency Check只比较：

`Contract Facts ↔ Actual Facts`

它不负责判断法定税务义务。

法定税务义务由Regulation Result、Rule Engine和Tax Judgement处理。

## 五、状态处理原则

### unknown

表示当前材料或法规不足，无法形成可靠结论。

unknown：

- 不等于违规
- 不等于已经完成
- 不等于没有完成
- 不允许被大模型强行改写为确定状态

### pending

表示按照当前交易阶段，事项尚未进入应发生阶段。

正式`actual_*`事件对象不保存pending状态。

### failed

failed表示模块发生技术错误。

业务上的unknown、partial、needs_review或材料缺失，不等于技术执行失败。

## 六、风险与评分流程

正式风险处理链路为：

`Judgement Resolution + Tax Impact + Actual Facts`

↓

`Risk Trigger Rules`

↓

`Risk Events`

↓

`Risk Merge和Risk Suppression`

↓

`Tax Health Score`

Risk Event不能直接由每条Atomic Rule随意生成。

Evidence missing、unknown或低Evidence Coverage不能直接生成正式Tax Health Risk。

Tax Health Score与Evidence Coverage必须分别计算：

- Tax Health Score反映已经确认的税务风险
- Evidence Coverage反映当前结论的证据支持程度

最终评分不能由大模型自由决定。

## 七、错误处理

各模块统一返回成功结果或以下错误结构：

```json
{
  "success": false,
  "error_code": "",
  "error_message": "",
  "failed_stage": ""
}
模块必须明确：

- Input Schema
- Output Schema
- Error Handling
- Mock Input
- Mock Output

## 八、测试与校验

项目使用以下测试方式：

- JSON Schema自动校验
- Rule Engine单元测试
- Risk Trigger测试
- 评分边界测试
- Golden Test Cases
- Dify与Rule Engine联调测试
- DeepSeek API连接测试

Golden Test锁定结构化业务结果，不要求大模型生成的自然语言逐字一致。

## 九、配置与安全

DeepSeek API配置通过本地`.env`文件读取。

`.env`和`.venv`不能上传到GitHub。

GitHub只保存：

- `.env.example`
- 程序代码
- Schema
- Prompt
- Registry
- Rule
- Mock
- Test
- Dify Workflow导出文件
- 项目文档

## 十、当前实施顺序

1. 将统一原则v0.6同步到Git
2. 确定JSON Schema v1.1
3. 冻结各类Registry
4. 冻结Risk Trigger Rules
5. 冻结Scoring Profile和Mapping Tables
6. 开发Rule Engine、Risk Trigger和评分模块
7. 编写Schema Validator和Golden Test Runner
8. 完成Dify与Rule Engine正式接线
9. 运行完整测试
10. 输出最终Workflow和技术文档