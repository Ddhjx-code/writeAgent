---
name: write-chapter
description: 执行单章完整创作流程。从场景规划到归档更新的全部步骤。
---

# /project:write-chapter N

参数N为章节编号，缺省则自动取outline.md中下一个未完成章节。

## 流程

### Step 1 场景规划（planner）
派planner执行"章节场景规划"任务：
- 读取本章大纲、前章正文、人物档案、悬念/伏笔追踪
- 产出场景序列、悬念伏笔规划、节奏设计
- 写入 plans/chNN-plan.md

主Agent更新outline.md中本章TODO状态为"进行中"。

### Step 2 写作（writer）
派writer执行"撰写章节"任务：
- 读取场景规划、人物档案、前章结尾
- 按chapter-template.md格式输出
- 写入 chapters/chNN.md

### Step 3 审查（reviewer）
派reviewer执行"章节审查"任务：
- 读取章节正文、场景规划、人物档案、悬念追踪
- 按review-report-template.md格式输出
- 写入 reviews/chNN-review.md

### Step 4 判断（主Agent）
读取审查报告，判断：

**通过**（≥35分，无单项≤2）→ 进入Step 5

**需修改** → 
- 将writer任务交给writer重写
- 重写后回到Step 3复审
- 同一章最多重试3次，仍不通过则向人类求助

**需重写**（<25分或核心维度≤1）→
- 交给writer完全重写
- 回到Step 3
- 最多重试3次

### Step 5 润色（polisher）
派polisher执行"审查后润色"任务：
- 读取章节正文和审查报告中polisher任务
- 润色后覆写 chapters/chNN.md
- 返回润色报告

### Step 6 归档（planner）
派planner执行"章节定稿后更新"任务：
- 更新人物状态、悬念追踪、伏笔追踪
- 更新大纲TODO状态为"已完成"，追加章节摘要
- 写入 bible/changelog.md

### Step 7 完成
主Agent向人类简要汇报：
- 本章完成，字数，核心事件一句话概括
- 如触发里程碑（章节号为5的倍数），提示进入里程碑审查
