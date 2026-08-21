# Tax Agent 技术节点图

```mermaid
flowchart TD
    A["用户上传材料（Dify User Input）"]
    B["遍历文件（List Operator / Iteration）"]
    C["提取文件文字（Document Extractor / OCR）"]
    D["文件分类（DeepSeek LLM）"]
    E["提取合同、履约和证据事实（DeepSeek LLM）"]
    F["字段规范化（Dify Code）"]
    G["合并 Transaction Facts 并校验 Schema（Dify Code）"]
    H{"关键事实是否完整？"}
    I["请求用户补充信息（Human Input）"]
    J["构造法规检索条件（Dify Code）"]
    K["按时间检索法规（Knowledge Retrieval）"]
    L["生成 Tax Judgement（DeepSeek LLM）"]
    M["一致性检查（LLM / Code）"]
    N["确定性评分（Python Rule Engine API）"]
    O["税务影响和下一步行动（Code）"]
    P["生成最终报告（DeepSeek LLM）"]
    Q["输出税务健康报告（Dify Output）"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H -- "不完整" --> I
    I --> G
    H -- "完整" --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    O --> P
    P --> Q
```

## 技术边界

- DeepSeek LLM：理解文件、提取事实、形成税务判断和解释报告。
- Dify Code：整理字段、合并 JSON、校验 Schema 和构造检索条件。
- Knowledge Retrieval：根据交易时间和业务类型检索法规。
- Python Rule Engine：计算健康分、证据完整度和风险等级。
- LLM 不得修改 Python Rule Engine 已经计算出的分数。