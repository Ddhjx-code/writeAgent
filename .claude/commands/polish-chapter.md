---
name: polish-chapter
description: 单独对已写章节执行润色，不触发重写。用于人类觉得内容可以但文字需要打磨时使用。
---

# /project:polish-chapter N

参数N为章节编号，必填。

## 前置检查
- 确认 chapters/chNN.md 存在，不存在则提示人类先写作
- 检查 reviews/chNN-review.md 是否存在：
  - 存在 → 执行审查后润色（使用报告中的polisher任务清单）
  - 不存在 → 执行全面润色

## 流程

### Step 1 润色（polisher）
派polisher执行对应类型的润色任务：
- 读取 chapters/chNN.md
- 如有审查报告，读取 reviews/chNN-review.md
- 读取 skills/shared/deai-rules.md
- 根据需要读取 dialogue-writing.md 或 description-craft.md
- 按优先级处理：去AI味 → 对话 → 描写 → 节奏 → 措辞
- 覆写 chapters/chNN.md
- 返回润色报告

### Step 2 汇报（主Agent）
向人类展示润色报告：
- 修改概要（每个方面做了什么）
- 超出润色范围的问题（如有）
- 润色后字数

### Step 3 提示后续
- 如有超出范围的问题 → 建议派writer处理
- 如需归档更新 → 提示执行归档
- 如满意 → 提示继续下一章
