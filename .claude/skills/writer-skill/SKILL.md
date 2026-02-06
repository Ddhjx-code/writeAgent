---
name: writer-skill
description: 写作技能包。用于撰写章节正文，涵盖章节结构、对话、描写、内容充实、文化符号等写作方法论。
---

# 写作技能包

[技能说明]
    章节写作技能，用于根据上下文包和场景规划撰写高质量章节正文。写作前必须读取相关技巧文件，按场景规划逐场景完成，写完后执行字数检查。

[文件结构]
    writer-skill/
    ├── SKILL.md                # 本文件
    ├── chapter-guide.md        # 章节结构与场景组织
    ├── dialogue-writing.md     # 对话写作策略
    ├── description-craft.md    # 描写与感官呈现
    ├── content-expansion.md    # 内容充实技巧
    ├── cultural-symbols.md     # 跨文化符号运用
    └── templates/
        └── chapter-template.md # 章节输出模板

    共享技能（按需读取）：
    - shared/deai-rules.md
    - shared/hook-techniques.md

[功能]
    [撰写章节]
        第一步：读取输入素材
            - 主Agent提供的"写作上下文包"
            - 主Agent提供的"场景规划"

        第二步：读取必要技巧文件
            - 读取 chapter-guide.md
            - 读取 shared/hook-techniques.md

        第三步：按需读取技巧文件
            根据本章内容特点选择：
            - 对话密集 → 读取 dialogue-writing.md
            - 环境/情感描写重 → 读取 description-craft.md
            - 涉及文化/历史元素 → 读取 cultural-symbols.md
            - 首次写作或曾被指出AI味 → 读取 shared/deai-rules.md

        第四步：读取模板
            - 读取 templates/chapter-template.md

        第五步：撰写正文
            - 按场景规划逐场景写作
            - 遵循 chapter-guide.md 的结构要求
            - 按模板格式输出

        第六步：字数检查
            - 执行字数检查脚本
            - 3000-5000字为合格范围
            - 不足3000字 → 读取 content-expansion.md 扩充
            - 扩充后再次检查

        第七步：写入文件
            - 写入 chapters/chNN-标题.md
            - 返回完成确认

    [扩充章节]
        当字数不足时触发：
        第一步：读取 content-expansion.md
        第二步：识别可扩充的场景或段落
        第三步：扩充后覆写章节文件
        第四步：再次执行字数检查

[注意事项]
    - 必读文件在第二步，按需文件在第三步，控制上下文长度
    - 不修改 bible/ 目录下任何文件
    - 不执行审查，专注写作
    - 场景规划是参考而非死板约束，可根据写作节奏微调
