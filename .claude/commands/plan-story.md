---
name: plan-story
description: 触发故事立项流程。与人类对话挖掘创意方向，构建大纲、人物和世界观。
---

# /project:plan-story

## 流程

### 第一阶段：创意挖掘
主Agent与人类开放对话，了解：
- 想写什么题材和类型
- 有什么灵感来源或核心概念
- 期望的风格和调性
- 目标读者和预期篇幅
- 任何已有的想法片段

这是开放对话，不是问卷。自然地聊，深入挖掘。

### 第二阶段：方向提案
基于对话内容，主Agent提出3个故事方向：
- 每个方向包含：一句话前提、核心冲突、调性描述
- 方向之间应有明显差异
- 人类选定一个方向（或混合、或提出新方向）

### 第三阶段：构建设定
人类确认方向后：

1. **派planner构建大纲**
   - 读取 planner-skill/SKILL.md
   - 读取 templates/outline-template.md
   - 产出完整大纲
   - 主Agent呈现给人类确认

2. **派planner设计人物**
   - 读取 templates/character-template.md
   - 产出人物档案和关系网
   - 主Agent呈现给人类确认

3. **派planner建立世界观**（如需要）
   - 产出世界观文件
   - 主Agent呈现给人类确认

### 第四阶段：大纲审查
1. 派reviewer审视大纲结构
2. 主Agent整合审查意见呈现给人类
3. 人类反馈后，派planner修改
4. 人类最终确认

### 第五阶段：初始化
planner将确认后的内容写入bible/：
- bible/plot/outline.md
- bible/characters/*.md
- bible/characters/relationships.md
- bible/worldbuilding/*（如有）
- bible/plot/suspense-tracker.md（初始化）
- bible/plot/foreshadow-tracker.md（初始化）
- bible/changelog.md（初始化）

完成后提示人类可以开始创作。
