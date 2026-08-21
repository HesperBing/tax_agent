# Rule Engine v0.1 技术说明

## 1. 本版范围

本版实现图片任务要求中的第一批确定性能力：

- Rule ID 唯一性与精确匹配；
- Atomic Rule 条件执行；
- `confirmed / provisional / unknown` 优先级收敛；
- confirmed 对 confirmed 冲突显式输出 `conflict`；
- Tax Health Score 五维加权；
- 单 Risk Event 的 Risk Level；
- Case Tax Health Score；
- Evidence Coverage 固定缺口模型；
- Formal Risk Codes 汇总；
- `unknown`、`pending` 与 Evidence Gaps 分流。

## 2. 关键边界

- `unknown` 不等于违规，也不等于已完成或未完成。
- `pending` 表示检查时点尚未到达，不进入正式 Actual Event 状态。
- missing/unknown Evidence 只影响 Evidence Coverage，不直接生成 Formal Risk Event。
- Tax Health Score 与 Evidence Coverage 独立。
- Risk Level 由未取整的单事件 loss 自动确定。
- Rule Engine Output 只保存 `rule_execution_results[]` 与 `judgement_resolution_results[]`。
- Score、Risk Event 和 Evidence Gap 按 Schema v1.1 保存到各自模块，不塞回 Rule Engine Output。

## 3. 评分公式

```text
weighted_severity
= tax_consequence_severity × 0.25
+ tax_amount_impact × 0.20
+ obligation_violation_severity × 0.30
+ duration_severity × 0.15
+ impact_scope × 0.10

health_score_loss = weighted_severity × 10
tax_health_score = floor(max(0, 100 - total_health_score_loss))
```

Risk Level：

```text
[0, 5)   → low
[5, 15)  → medium
[15, 25) → high
[25, +∞) → critical
```

## 4. Evidence Coverage

```text
provided       → state_factor = 0
unknown        → state_factor = 0.5
missing        → state_factor = 1
not_applicable → 不评分
未来无 State   → 不评分
```

```text
instance_loss = configured_loss × state_factor
evidence_coverage = floor(max(0, 100 - min(100, Σ instance_loss)))
```

## 5. 当前 Rule 文件的定位

`rules/tax/atomic_rules_v0_1.json` 是接口联调和单元测试用的第一批规则。正式 Rule ID 一经业务负责人冻结后不得随意改名，删除后不得复用；新增正式规则时必须同步更新 Mock、测试和 CHANGELOG。

## 6. 下一版工作

- 将业务负责人冻结的全部 Atomic Rules 写入规则表；
- 实现五种固定 Risk Trigger Pattern；
- 完成 Risk Merge、Consequence Suppression 与更完整的 impact-group 去重；
- 接入真实对象仓库替换测试用内存 Context；
- 增加 Golden Test Runner 和 Dify Tool API 包装层。
