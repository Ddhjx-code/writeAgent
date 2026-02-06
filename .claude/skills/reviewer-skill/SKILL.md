---
name: reviewer-skill
description: 审查技能包。用于审查章节质量，从叙事逻辑、人物一致性、节奏体验、描写质量、对话质量、去AI味等维度进行检查，输出审查报告和修改建议。
---

# 审查技能包

[技能说明]
    章节审查技能，用于在章节写作完成后进行质量检查。审查覆盖多个维度，输出结构化的审查报告，并判断问题应由writer还是polisher处理。

[文件结构]
    reviewer-skill/
    ├── SKILL.md                  # 本文件
    ├── review-checklist.md       # 审查清单与评分维度
    ├── quality-standards.md      # 质量标准定义
    └── templates/
        └── review-report-template.md  # 审查报告模板

    共享技能（审查时参考）：
    - shared/deai-rules.md
    - shared/hook-techniques.md

[功能]
    [审查章节]
        第一步：读取输入
            - 待审查的章节正文
            - 该章的场景规划（来自researcher产出）
            - 该章涉及的人物档案（来自bible）

        第二步：读取审查标准
            - 读取 review-checklist.md
            - 读取 quality-standards.md

        第三步：按需读取参考文件
            - 检查AI味时参考 shared/deai-rules.md
            - 检查钩子和悬念时参考 shared/hook-techniques.md

        第四步：读取模板
            - 读取 templates/review-report-template.md

        第五步：逐维度审查
            按 review-checklist.md 中定义的维度逐项检查，
            每个维度给出：
            - 评分（1-5分）
            - 问题描述（如有）
            - 具体位置（引用原文）
            - 修改建议

        第六步：判断处理方
            对每个问题判断应由谁处理：
            - writer：结构性问题、内容缺失、逻辑错误、场景重写
            - polisher：语言润色、措辞调整、AI味清除、微调节奏

        第七步：生成报告
            按模板格式输出审查报告，包括：
            - 总评分
            - 各维度评分和问题
            - 修改建议清单（标注处理方）
            - 审查结论（通过/需修改/需重写）

        第八步：写入文件
            - 写入 reviews/chNN-review.md
            - 返回完成确认

    [复审章节]
        当章节经过修改后再次提交审查时触发：
        第一步：读取修改后的章节和上一份审查报告
        第二步：检查上一份报告中的问题是否已解决
        第三步：检查修改是否引入了新问题
        第四步：生成复审报告
        第五步：写入 reviews/chNN-review-v2.md

[审查结论标准]
    通过：总分≥35分（满分50分），无单项≤2分
    需修改：总分25-34分，或有单项≤2分但整体可救
    需重写：总分<25分，或核心维度（叙事逻辑/人物一致性）≤1分

[注意事项]
    - reviewer只输出报告，不直接修改章节
    - 审查应基于客观标准，避免主观偏好
    - 问题描述要具体，引用原文位置，不说"整体感觉不好"
    - 修改建议要可执行，不说"写得更好一点"
    - 不修改 bible/ 目录下任何文件
