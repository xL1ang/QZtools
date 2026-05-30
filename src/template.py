"""模板加载与变量替换。"""

from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
SEPARATOR = "=" * 64


def load_template(name: str) -> str:
    """加载 src/templates/ 下的模板文件。"""
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"模板文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def render(template_text: str, variables: dict[str, str]) -> str:
    """将模板中的 {{变量名}} 替换为实际内容。

    只替换变量区域（🔒区域）中的占位符，
    提示词区域（✏️区域）原样保留作为 prompt 的一部分。
    """
    for key, value in variables.items():
        template_text = template_text.replace(f"{{{{{key}}}}}", value)
    return template_text


def extract_prompt(rendered_text: str) -> str:
    """从渲染后的模板中提取完整内容作为 prompt 发送给 LLM。

    去掉分隔线标记，保留所有文字内容。
    """
    lines = rendered_text.split("\n")
    result = []
    for line in lines:
        if line.strip().startswith(SEPARATOR):
            continue
        if line.strip().startswith("🔒") or line.strip().startswith("✏️"):
            continue
        result.append(line)
    return "\n".join(result).strip()
