# 需求分析 Agent 规格说明

## 项目背景

晴子（亮的同事，NVR 项目）需要一个工具，帮助她从参考文档 + 新需求 → 自动生成结构化方案文档 + 页面原型。

---

## ✅ 已敲定

### 1. 技术栈
- **语言：** Python
- **包管理/环境隔离：** uv（`pyproject.toml` + lock 文件，跨平台）
- **版本管理：** Git
- **目标平台：** Windows（晴子的办公电脑），Linux 下开发和调试

### 2. 目录结构

```
需求分析Agent/
├── .gitignore
├── pyproject.toml
├── config.yaml              # API 配置
├── input/
│   ├── existing-logic/      # 1. 现有功能逻辑文档
│   ├── interfaces/          # 2. 关联模块接口文档
│   ├── prototypes/          # 3. 当前页面参考原型
│   └── format-standards/    # 4. 输出格式标准
├── output/                  # AI 生成的方案 & 原型
└── src/                     # 代码 + prompt 模板
    ├── main.py
    ├── reader.py
    ├── analyzer.py
    ├── prototyper.py
    └── templates/           # prompt 模板
```

### 3. API 配置（config.yaml）

```yaml
use_provider: "deepseek"  # 填 claude / openai / deepseek，三选一

providers:
  claude:
    api_key: "***"
    base_url: "https://api.anthropic.com"
    model: "claude-sonnet-4-20250514"
  openai:
    api_key: "***"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
  deepseek:
    api_key: "***"
    base_url: "https://api.deepseek.com"
    model: "deepseek-chat"
```

- 只填要用的那个就行，多余的可删可不删
- Agent 根据 `use_provider` 定位对应配置
- 用户自己管理 key，不依赖亮的 API 服务器

### 4. Reader 模块支持的文件格式（首版）

| 格式 | 解析方式 | 优先级 |
|------|---------|--------|
| `.md` / `.txt` | 原生 `open()` | 首版 |
| `.docx` | `python-docx` | 首版 |
| `.pdf` | `pymupdf` | 首版 |
| `.xlsx` | `openpyxl` | 首版 |
| 图片 (png/jpg) | 首版跳过，后续支持多模态 | 后续 |

- Reader 暴力遍历 input 子文件夹，自动识别格式，统一拼成文本上下文
- 首版遇到图片文件直接忽略

### 5. 晴子的操作流程
1. `git clone`
2. 四种参考文档分别丢进 `input/` 的四个子文件夹
3. 填 `config.yaml` 的 `api_key` + `use_provider`
4. `uv run src/main.py`
5. 按交互引导完成整个流程
6. 去 `output/` 拿结果

### 6. 工作流（三阶段）

**第一阶段 — 读取上下文**
- 读取四个 input 子文件夹中的所有文档
- 格式统一为文本后拼成 LLM 上下文

**第二阶段 — 需求分析 + 方案生成（人机交互）**
1. 人工输入本次新需求 → AI 输出：
   - 需要调整的模块
   - 每个模块的基础方案 + 风险点
2. 人工确认后，AI 进一步输出每个模块的结构化内容：
   - 列表页、详情页
   - 业务流程
   - 计算逻辑
   - 外部系统对接接口入参/出参
   - 单据流转状态机
   - 系统交互时序图
3. 人工审核调整方案

**第三阶段 — 原型生成**
- 根据最终方案 + 参考原型 → AI 生成新页面原型

---

### 7. Prompt 设计

- **格式：** `.md` 文件，存放在 `src/templates/`
- **变量：** `{{变量名}}`，代码侧纯字符串替换，无模板引擎依赖
- **分区：** 每个模板分为 🔒变量区域（不可改）和 ✏️提示词区域（可自由修改）
- **原则：** 首版提供简单骨架 prompt，晴子自己根据效果迭代

模板文件：
```
src/templates/
├── stage1_context.md      # 阶段一：上下文整理
├── stage2_analyze.md      # 阶段二-1：需求拆解
├── stage2_detail.md       # 阶段二-2：方案细化
└── stage3_prototype.md    # 阶段三：原型生成
```

### 8. 输出格式

| 输出内容 | 格式 | 文件名 |
|---------|------|--------|
| 系统现状摘要 | Markdown | `output/context_summary.md` |
| 模块分析 | Markdown | `output/module_analysis.md` |
| 详细方案 | Markdown（含 Mermaid 图 + 中文描述） | `output/detailed_plan.md` |
| 页面原型描述 | Markdown | `output/prototype.md` |
| 页面原型 | HTML | `output/<page_name>.html` |

- 状态机/时序图：中文文字描述 + Mermaid 代码块，都写在 .md 中
- 目录名和文件名统一英文

### 9. Agent 工作样态

- **交互方式：** 纯 CLI 问答式，线性流程
- **中间结果：** 终端打印进度摘要，完整内容实时写入 `output/` 文件
- **重新生成：** 支持（确认环节提供选项：确认 / 调整意见 / 重新生成）
- **断点续作：** 首版不做（每步已写入文件，重跑代价不大）
- **错误处理：** LLM 调用失败自动重试 2 次，仍失败则打印错误原因并提示检查 API key/网络

### 10. 代码设计

```
src/
├── main.py          # 入口，编排三阶段流程 + CLI 交互
├── reader.py        # 遍历 input/，解析多格式文件，拼成文本
├── analyzer.py      # 阶段1&2：调 LLM 生成摘要/分析/方案
├── prototyper.py    # 阶段3：调 LLM 生成原型描述 + HTML
├── llm_client.py    # 统一 LLM 调用（OpenAI SDK 格式，适配三家 API）
├── template.py      # 加载 .md 模板 + {{变量}} 替换
└── templates/       # prompt 模板文件
```

- LLM 调用统一走 OpenAI SDK `/v1/chat/completions` 格式
- DeepSeek / OpenAI 原生兼容，Claude 走兼容模式
- 切换 provider 只需改 config.yaml 中的 `use_provider`
- reader.py 返回 dict：`{"existing_logic": "...", "interfaces": "...", ...}`
- analyzer.py 和 prototyper.py 职责分离
