# 需求分析 Agent

从参考文档 + 新需求 → 自动生成结构化方案文档 + 页面原型。

## 安装环境

1. 打开 PowerShell（按 Win 键，输入 `powershell`，回车）
2. 安装 uv：
   ```
   irm https://astral.sh/uv/install.ps1 | iex
   ```
3. 关闭 PowerShell，重新打开一个

## 使用步骤

1. 把参考文档分别放进对应文件夹：
   - `input/existing-logic/` — 现有功能逻辑文档
   - `input/interfaces/` — 关联模块接口文档
   - `input/prototypes/` — 当前页面参考原型
   - `input/format-standards/` — 输出格式标准

2. 打开 `config.yaml`，填写你的 API 密钥：
   ```yaml
   use_provider: "deepseek"
   providers:
     deepseek:
       api_key: "在这里填你的密钥"
   ```

3. 在项目文件夹打开 PowerShell，运行：
   ```
   uv run src/main.py
   ```

4. 按提示操作，结果在 `output/` 文件夹中。

## 调整 AI 效果

打开 `src/templates/` 下的 `.md` 文件，修改 ✏️ 区域的文字即可。

🔒 区域不要动，是程序自动填充的变量。
