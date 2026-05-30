"""阶段 3：原型生成 — 文字描述 + HTML 页面。"""

import re
from pathlib import Path

from . import llm_client, template

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def ensure_output_dir():
    """确保 output/ 目录存在。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def stage3_prototype(final_plan: str, prototypes: str) -> str:
    """阶段三：根据最终方案 + 参考原型生成页面原型描述。"""
    ensure_output_dir()

    tmpl = template.load_template("stage3_prototype.md")
    rendered = template.render(
        tmpl,
        {
            "final_plan": final_plan,
            "prototypes": prototypes,
        },
    )
    prompt = template.extract_prompt(rendered)

    print("[阶段三] 正在生成页面原型描述...")
    result = llm_client.chat(prompt)

    output_path = OUTPUT_DIR / "prototype.md"
    output_path.write_text(result, encoding="utf-8")
    print(f"  [OK] 已保存 {output_path}")

    return result


def generate_html(final_plan: str, prototype_desc: str) -> list[str]:
    """根据方案和原型描述，逐页让 LLM 生成 HTML 页面文件。"""
    ensure_output_dir()

    # 第一步：让 LLM 列出需要生成的页面清单
    list_prompt = (
        "根据以下方案，列出需要生成的页面名称（每行一个，只输出页面名，不要其他内容）：\n\n"
        f"{final_plan}"
    )

    print("[阶段三] 正在分析需要生成的页面...")
    page_list_text = llm_client.chat(list_prompt)
    page_names = [
        line.strip() for line in page_list_text.strip().split("\n") if line.strip()
    ]

    if not page_names:
        print("  [..] 未能识别出需要生成的页面")
        return []

    print(f"  [OK] 识别到 {len(page_names)} 个页面: {', '.join(page_names)}")

    # 第二步：逐页生成 HTML
    saved_files = []
    for i, page_name in enumerate(page_names, 1):
        prompt = (
            "你是一个前端原型生成助手。\n\n"
            "## 方案\n\n"
            f"{final_plan}\n\n"
            "## 页面原型描述\n\n"
            f"{prototype_desc}\n\n"
            "## 任务\n\n"
            f"请只生成【{page_name}】这一个页面的 HTML 代码。\n"
            "要求：\n"
            "- 使用简洁的内联 CSS，不依赖外部资源\n"
            "- 包含页面标题、字段、按钮等基本元素\n"
            "- 体现页面布局和交互说明\n\n"
            "直接输出完整的 HTML 代码，不要用 ``` 包裹。\n"
        )

        print(f"  [{i}/{len(page_names)}] 正在生成: {page_name}...")
        html_content = llm_client.chat(prompt)

        # 清理可能的 ``` 包裹
        html_content = strip_code_fence(html_content)

        # 生成安全的文件名
        filename = sanitize_filename(page_name) + ".html"
        output_path = OUTPUT_DIR / filename
        output_path.write_text(html_content, encoding="utf-8")
        saved_files.append(str(output_path))
        print(f"  [OK] 已保存 {output_path}")

    return saved_files


def strip_code_fence(text: str) -> str:
    """去掉 LLM 输出中可能包裹的 ``` 代码围栏。"""
    text = text.strip()
    if text.startswith("```html"):
        text = text[len("```html") :]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def sanitize_filename(name: str) -> str:
    """将页面名转成安全的文件名（英文/拼音，去掉特殊字符）。"""
    # 保留字母数字下划线横杠中文
    safe = re.sub(r"[^\w\u4e00-\u9fff\-]", "_", name)
    return safe.strip("_") or "page"
