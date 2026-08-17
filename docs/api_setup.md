# DeepSeek API 环境准备说明

## 一、模型配置

```text
Provider: DeepSeek
Base URL: https://api.deepseek.com
Model: deepseek-v4-flash
```

## 二、相关文件

- `.env.example`：环境变量模板，不包含真实密钥。
- `.gitignore`：禁止上传 `.env` 和 `.venv`。
- `requirements.txt`：Python 依赖清单。
- `tests/test_deepseek_api.py`：API 连接测试程序。

## 三、本地配置方法

根据 `.env.example` 在项目根目录创建 `.env`：

```env
DEEPSEEK_API_KEY=填写自己的API_Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

真实 API Key 不得上传 Git。

## 四、安装依赖

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 五、测试连接

```powershell
.\.venv\Scripts\python.exe tests\test_deepseek_api.py
```

预期结果：

```text
API 调用成功
模型：deepseek-v4-flash
回答：DeepSeek API 连接成功
```

## 六、安全要求

- 不在代码中直接填写 API Key。
- 不上传 `.env`。
- 不上传 `.venv`。
- 不在截图或文档中展示真实 API Key。