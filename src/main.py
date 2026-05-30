"""需求分析 Agent 入口 — 编排三阶段流程 + CLI 交互。"""

from src import analyzer, prototyper, reader


def get_user_input(prompt_text: str) -> str:
    """获取用户多行输入，空行结束。"""
    print(prompt_text)
    print("(输入完成后按两次回车)")
    lines = []
    empty_count = 0
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 1 and lines:
                break
            lines.append("")
        else:
            empty_count = 0
            lines.append(line)
    return "\n".join(lines).strip()


def confirm_step() -> str:
    """让用户确认当前步骤结果。

    返回: "confirm" / "adjust" / "regenerate"
    """
    while True:
        print("\n请查看输出文件，选择操作：")
        print("  [1] 确认，继续下一步")
        print("  [2] 我有调整意见")
        print("  [3] 不满意，重新生成")
        choice = input("> ").strip()
        if choice == "1":
            return "confirm"
        elif choice == "2":
            return "adjust"
        elif choice == "3":
            return "regenerate"
        else:
            print("请输入 1、2 或 3")


def main():
    print("=" * 50)
    print("  需求分析 Agent")
    print("=" * 50)

    # --- 阶段一：读取上下文 ---
    print("\n[阶段一] 正在读取 input/ 文件夹...")
    inputs = reader.read_all_inputs()

    # 检查是否有内容
    total_files = sum(1 for v in inputs.values() if v.strip())
    if total_files == 0:
        print("[错误] input/ 文件夹中没有找到任何文档。")
        print("请将参考文档放入 input/ 的子文件夹中后重试。")
        return

    for folder_name, content in inputs.items():
        status = "[OK]" if content.strip() else "[空]"
        print(f"  {status} {folder_name}")

    context_summary = analyzer.stage1_context(inputs)

    # --- 阶段二-1：需求拆解 ---
    user_requirement = get_user_input("\n[阶段二] 请输入本次新需求：")
    if not user_requirement:
        print("[错误] 未输入需求内容，退出。")
        return

    while True:
        module_analysis = analyzer.stage2_analyze(context_summary, user_requirement)
        action = confirm_step()
        if action == "confirm":
            break
        elif action == "adjust":
            user_requirement = get_user_input("请输入调整后的需求或补充说明：")
        # action == "regenerate" 则循环重新生成

    # --- 阶段二-2：方案细化 ---
    user_feedback = ""
    while True:
        detailed_plan = analyzer.stage2_detail(
            context_summary, user_requirement, module_analysis, user_feedback
        )
        action = confirm_step()
        if action == "confirm":
            break
        elif action == "adjust":
            user_feedback = get_user_input("请输入你的调整意见：")
        # action == "regenerate" 则循环重新生成

    # --- 阶段三：原型生成 ---
    prototype_desc = prototyper.stage3_prototype(detailed_plan, inputs["prototypes"])

    while True:
        prototyper.generate_html(detailed_plan, prototype_desc)
        action = confirm_step()
        if action == "confirm":
            break
        elif action == "adjust":
            feedback = get_user_input("请输入你对原型的调整意见：")
            prototype_desc = prototype_desc + "\n\n## 用户调整意见\n\n" + feedback
        # action == "regenerate" 则循环重新生成

    # --- 完成 ---
    print("\n" + "=" * 50)
    print("  全部完成！结果在 output/ 文件夹中。")
    print("=" * 50)


if __name__ == "__main__":
    main()
