---
name: review-milestone
description: 触发里程碑审查。每5章自动触发或人类手动触发，汇报全局进度并获取反馈。
---

# /project:review-milestone

无需参数，自动检测当前进度。

## 流程

### Step 1 进度汇总（planner）
派planner执行"进度汇总"任务：
- 读取 bible/plot/outline.md（TODO状态、章节摘要）
- 读取 bible/plot/suspense-tracker.md
- 读取 bible/plot/foreshadow-tracker.md
- 读取 bible/changelog.md（最近更新）
- 汇总最近5章（或自上次里程碑以来）的进展

### Step 2 一致性检查（planner）
派planner执行"一致性检查"任务：
- 通读bible所有文件
- 检查人物、世界观、悬念、伏笔的一致性
- 输出一致性检查报告

### Step 3 汇报（主Agent）
向人类展示：
- 已完成章节概要（每章一句话）
- 当前剧情走向与大纲的偏差（如有）
- 角色发展是否符合预期
- 悬念/伏笔状态（活跃多少、已回收多少、超期多少）
- 一致性问题（如有）
- 接下来5章的大纲预览
- 完成进度百分比

### Step 4 等待人类反馈
提示可选操作：
- 继续创作 → 回到逐章创作流程
- 调整大纲 → 派planner修改outline.md
- 修改某章 → 进入回退流程
- 调整人物 → 派planner更新人物档案
- 其他反馈 → 主Agent记录并处理
