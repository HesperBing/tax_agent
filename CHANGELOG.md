# Change Log

## v0.1 - 2026-08-16

- 建立项目 Git 仓库。
- 添加统一原则文档。
- 建立项目基础目录。
- 配置 DeepSeek API 环境并完成连接测试。
- 添加 Tax Agent 技术节点图。
- 添加 Dify Workflow v0.1 技术规划和节点清单。

## v0.6 - 2026-08-21

- 修改人：成员C
- 修改原因：项目内容和统一原则升级至v0.6

### 修改内容

- 将当前统一原则更新为v0.6
- 归档旧版统一原则和旧版技术架构
- 更新技术架构为严格单向工作流
- 新增Dify Workflow v0.6技术规划
- 取消补充问答和用户自然语言事实输入
- 新增Actual Tax Treatment和Actual Obligation State设计
- 新增Risk Trigger、Risk Event和评分Mapping设计
- 新增`registries/`和`scoring/`目录
- 将`rules/`细分为tax、risk、evidence和consistency
- 确定后续接口使用JSON Schema v1.1
- 更新README项目说明和当前进度

### 影响模块

- docs
- dify
- schemas
- registries
- rules
- rule_engine
- scoring
- mocks
- tests
- prompts

### 后续处理

- Schema是否已经完成更新：否，待后续编写
- Mock是否已经完成更新：否，待后续编写
- Golden Test是否已经完成更新：否，待后续建立
- 是否需要重新测试：是
- 当前DeepSeek API连接测试：已通过