"""阶段 1 & 2：上下文整理 + 需求分析 + 方案细化。"""

from pathlib import Path

from . import llm_client, template

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def ensure_output_dir():
    """确保 output/ 目录存在。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def stage1_context(inputs: dict[str, str]) -> str:
    """阶段一：读取所有文档，生成系统现状摘要。"""
    ensure_output_dir()

    tmpl = template.load_template("stage1_context.md")
    rendered = template.render(tmpl, inputs)
    prompt = template.extract_prompt(rendered)

    print("[阶段一] 正在生成系统现状摘要...")
    result = llm_client.chat(prompt)

    output_path = OUTPUT_DIR / "context_summary.md"
    output_path.write_text(result, encoding="utf-8")
    print(f"  [OK] 已保存 {output_path}")

    return result


def stage2_analyze(context_summary: str, user_requirement: str) -> str:
    """阶段二-1：需求拆解，输出受影响模块 + 方案 + 风险。"""
    ensure_output_dir()

    tmpl = template.load_template("stage2_analyze.md")
    rendered = template.render(
        tmpl,
        {
            "context_summary": context_summary,
            "user_requirement": user_requirement,
        },
    )
    prompt = template.extract_prompt(rendered)

    print("[阶段二-1] 正在分析需求...")
    result = llm_client.chat(prompt)

    output_path = OUTPUT_DIR / "module_analysis.md"
    output_path.write_text(result, encoding="utf-8")
    print(f"  [OK] 已保存 {output_path}")

    return result


def stage2_detail(
    context_summary: str,
    user_requirement: str,
    module_analysis: str,
    user_feedback: str,
) -> str:
    """阶段二-2：方案细化，输出每个模块的结构化详细方案。"""
    ensure_output_dir()

    tmpl = template.load_template("stage2_detail.md")
    rendered = template.render(
        tmpl,
        {
            "context_summary": context_summary,
            "user_requirement": user_requirement,
            "module_analysis": module_analysis,
            "user_feedback": user_feedback,
        },
    )
    prompt = template.extract_prompt(rendered)

    print("[阶段二-2] 正在生成详细方案...")
    result = llm_client.chat(prompt)

    output_path = OUTPUT_DIR / "detailed_plan.md"
    output_path.write_text(result, encoding="utf-8")
    print(f"  [OK] 已保存 {output_path}")

    return result
