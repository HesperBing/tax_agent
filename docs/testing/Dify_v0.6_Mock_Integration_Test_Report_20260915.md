# Tax Agent Dify v0.6 Mock 集成测试报告

## 1. 基本信息

- 测试日期：2026-09-15
- 测试人员：同学 C
- 应用名称：`Tax Agent Main Workflow v0.6 - Mock Integration`
- 统一规范版本：v0.6
- JSON Schema：v1.1
- Rule Engine：v0.1
- 最终 DSL：`Tax Agent Main Workflow v0.6 - Mock Integration.yml`
- 测试性质：Dify 工作流结构、变量接口、条件分支与 Mock 数据联调

## 2. 测试结论

**结论：Mock 集成验收通过（PASS）。**

工作流能够完成文件输入、文档提取与分类、事实 Mock 接入、多合同判断、多合同证据链、链条指标、法规检索 Mock、税务判断 Mock、Rule Engine Mock 以及最终输出。最终测试共执行 15 个步骤，全部成功。

本结论仅代表接口与流程联调通过，不代表真实税务结论已完成，也不代表所有法规、税率、申报期限和税额已经核验。

## 3. 最终验收结果

| 项目 | 结果 |
| --- | --- |
| 运行状态 | SUCCESS |
| 运行时间 | 5.357 秒 |
| Token 数 | 2616 |
| 运行步骤 | 15 |
| 合同数量 | 3 |
| 多合同判断 | `true` |
| 工作流路由 | `multi_contract_chain` |
| 证据链状态 | `complete_needs_review` |
| 链条指标状态 | `complete_needs_review` |
| Knowledge Retrieval 状态 | `complete_needs_review` |
| Tax Judgement 状态 | `partial` |
| Rule Engine 状态 | `complete_needs_review` |
| 风险等级 | `low`（仅表示没有已确认风险） |
| 风险代码 | `[]` |
| Tax Health Score | 100 |
| Evidence Coverage | 100 |

## 4. 已验证节点

1. 用户输入
2. 文档提取器
3. 文件分类迭代
4. 分类结果代码处理与条件分支
5. Facts Mock 接入
6. Transaction Facts Mock 接入
7. 合同数量判断
8. 多合同条件分支
9. 多合同证据链 Mock
10. 多合同链条指标 Mock
11. Knowledge Retrieval Mock 接入
12. Tax Judgement Mock 接入
13. Rule Engine Mock 接入
14. 最终正常输出
15. 最终异常输出路径配置检查

## 5. 核心接口结果

### 5.1 交易事实

- Tax Case：`TC-TAX-CROSS-001`
- Transaction Fact：`TRANSACTION-TC-TAX-CROSS-001`
- Economic Substance：`technical_consulting`
- Contract Fact 引用：CT01、CT02、CT03
- Actual Acceptance 引用：CT01、CT02、CT03

### 5.2 多合同链

- 合同链：`CONTRACT-CHAIN-TC-TAX-CROSS-001`
- 合同节点：3 个
- 候选关联边：2 条
- 合并合同金额：1,140,000 CNY
- 收入、成本、隐藏利润：保持 `null`，等待事实补充和人工复核

### 5.3 法规与判断

- 法规引用：`LAW_VAT_H001`
- 文件：财税〔2016〕36号
- 适用性结果：`candidate_applicable`
- 解决状态：`needs_review` / `insufficient`
- 未确认字段保持 `unknown`，未被当作违规

### 5.4 评分

- Tax Health Score 100：当前没有已确认风险事件，因此没有扣分；不等于案例已确认无风险。
- Evidence Coverage 100：当前登记的 `contract_performance_evidence` 状态为 `provided`；不表示所有可能材料均已收齐。

## 6. DSL 安全与结构检查

- 应用名称已更新为 v0.6。
- DSL 结构可正常解析。
- 节点数：18。
- 连线数：17。
- 断裂连线：0。
- HTTP 请求节点：0。
- Secret 环境变量：0。
- 未发现导出的 API Key、Bearer Token 或其他明文凭证。
- 未发现名称中仍含“占位”的节点。

## 7. 当前限制

以下模块目前使用 Mock，不得作为生产税务结论：

- Facts
- Transaction Facts
- 多合同证据链与链条指标
- Knowledge Retrieval / Temporal RAG
- Tax Judgement
- Rule Engine

真实接口接入后必须重新执行 Schema 校验、Golden Test Case 自动对比及至少一次生产候选版端到端回归测试。

## 8. 后续交付任务

1. 将最终 DSL 上传到仓库的 `dify/workflows/` 目录。
2. 将本报告上传到 `docs/testing/` 目录。
3. 在 README 中注明当前版本为 Mock Integration，不是生产税务判断版本。
4. 等待其他成员交付真实 Facts、Temporal RAG、Tax Judgement 和 Rule Engine 接口。
5. 替换 Mock 后执行 JSON Schema v1.1 校验。
6. 执行 Golden Test Cases 自动比较，保存 PASS/FAIL、差异和运行日志。
7. 仅在真实节点全部接入后进行一次完整材料回归，避免重复消耗 Token。

## 9. 建议 GitHub 路径

```text
dify/workflows/Tax_Agent_Main_Workflow_v0.6_Mock_Integration.yml
docs/testing/Dify_v0.6_Mock_Integration_Test_Report_20260915.md
```

