---
name: review-chapter
description: 单独对已写章节执行审查，不触发写作。用于人类想针对某章获取审查意见时使用。
---

# /project:review-chapter N

参数N为章节编号，必填。

## 前置检查
- 确认 chapters/chNN.md 存在，不存在则提示人类先写作
- 确认相关人物档案存在

## 流程

### Step 1 审查（reviewer）
派reviewer执行"章节审查"任务：
- 读取 chapters/chNN.md
- 读取 plans/chNN-plan.md（如存在）
- 读取相关人物档案
- 读取前一章结尾（如非第一章）
- 读取 bible/plot/suspense-tracker.md
- 按十个维度逐项检查
- 按 review-report-template.md 格式输出
- 写入 reviews/chNN-review.md

### Step 2 汇报（主Agent）
读取审查报告，向人类展示：
- 总分和审查结论
- 各维度评分概览
- 主要问题清单（按严重程度排列）
- 优点

### Step 3 等待人类决策
提示可选操作：
- 接受审查，继续润色 → 执行 /project:polish-chapter N
- 交给writer修改 → 派writer修改后重新审查
- 忽略审查意见，保持原文
- 人类自行修改后重新审查
