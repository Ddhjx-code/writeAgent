# 📚 AI小说创作系统

基于Claude Code的多Agent协作小说创作框架。通过四个专业子Agent分工协作，在人类作家的创意指导下完成长篇小说的规划、写作、审查和润色。

## 核心理念

- **人类主导创意**：AI负责执行，人类负责方向
- **分工协作**：四个子Agent各司其职，主Agent协调全局
- **文件即记忆**：所有信息持久化到文件，不依赖对话上下文
- **质量闭环**：每章经过 规划→写作→审查→润色→归档 完整流程

## 团队分工

主Agent（编剧）负责全局协调，派遣四个专业子Agent执行具体工作：

| 角色 | 职责 | 可读 | 可写 |
|------|------|------|------|
| **planner** | 规划与归档：大纲、人物、世界观、场景规划、bible维护 | 全部文件 | bible/, plans/ |
| **writer** | 写作：根据场景规划撰写章节正文 | 技能包, bible, plans | chapters/ |
| **reviewer** | 审查：十维度质量检查，输出审查报告 | 全部文件 | reviews/ |
| **polisher** | 润色：去AI味、语言精修、节奏微调 | chapters, reviews, 技能包 | chapters/ |

## 项目结构

```
project/
├── .claude/
│ └── CLAUDE.md # 主Agent指令
├── skills/ # 技能包
│ ├── writer-skill/ # 写作技能
│ │ ├── SKILL.md # 技能主文件
│ │ ├── dialogue-writing.md # 对话写作规范
│ │ ├── description-craft.md # 描写技巧
│ │ └── content-expansion.md # 内容扩充策略
│ ├── reviewer-skill/ # 审查技能
│ │ ├── SKILL.md # 技能主文件
│ │ ├── review-checklist.md # 十维度审查清单
│ │ └── quality-standards.md # 质量分级标准
│ ├── polisher-skill/ # 润色技能
│ │ └── SKILL.md # 技能主文件
│ ├── planner-skill/ # 规划与归档技能
│ │ ├── SKILL.md # 技能主文件
│ │ ├── archive-maintenance.md # 归档维护规范
│ │ └── templates/
│ │ ├── outline-template.md # 大纲模板
│ │ └── character-template.md # 人物档案模板
│ └── shared/ # 共享技能
│ ├── hook-techniques.md # 钩子与悬念技巧
│ └── deai-rules.md # 去AI味规则
├── templates/ # 输出模板
│ ├── chapter-template.md # 章节输出格式
│ └── review-report-template.md # 审查报告格式
├── bible/ # 故事圣经（创作后生成）
│ ├── characters/ # 人物档案
│ ├── worldbuilding/ # 世界观设定
│ ├── plot/ # 情节记录
│ └── changelog.md # 更新日志
├── plans/ # 场景规划（创作后生成）
├── chapters/ # 定稿正文（创作后生成）
├── reviews/ # 审查报告（创作后生成）
└── README.md # 本文件
```


## 工作流程

### 整体流程

立项 → 大纲审查 → 逐章创作（循环） → 里程碑审查（每5章） → 全书收尾

> 里程碑审查后如需调整大纲，回到大纲审查步骤。

### 单章创作流程

| 步骤 | 执行者 | 任务 | 输出 |
|------|--------|------|------|
| Step 1 | planner | 场景规划 | plans/chNN-plan.md |
| Step 2 | writer | 写作 | chapters/chNN.md |
| Step 3 | reviewer | 审查 | reviews/chNN-review.md |
| Step 4 | 主Agent | 判断（通过/需修改/需重写） | — |
| Step 5 | polisher | 润色 | 覆写 chapters/chNN.md |
| Step 6 | planner | 归档更新 | 更新 bible/ |

### 人机协同节点

以下节点会暂停等待人类确认，其余环节自动推进：

| 节点 | 时机 | 人类决策 |
|------|------|----------|
| 故事立项 | 创作前 | 确认前提、题材、风格 |
| 大纲确认 | 规划后 | 确认章节大纲和角色设定 |
| 里程碑审查 | 每5章 | 方向调整、质量反馈 |
| 重大转折 | 关键剧情前 | 确认重大剧情走向 |
| 全书完结 | 最终章后 | 确认结局满意度 |

## 快速开始

### 前置要求

- Claude Code（支持Task工具和技能包系统）

### 启动

1. 克隆本项目
2. 在Claude Code中打开项目目录
3. 开始对话，主Agent会自动检测项目状态并引导你

### 首次使用

主Agent会自动检测到项目尚未立项，引导你进入立项流程：

1. **开放对话**：和主Agent聊你想写什么样的故事
2. **选择方向**：主Agent会提出3个故事方向供你选择
3. **确认设定**：确认大纲、人物、世界观
4. **开始创作**：确认后自动进入逐章创作流程

### 中断恢复

所有状态保存在文件中，随时可以：
- 关闭对话窗口，下次打开自动恢复进度
- 主Agent会读取outline.md的TODO清单定位当前进度

## 审查体系

reviewer从十个维度审查每个章节：

| 维度 | 权重 | 说明 |
|------|------|------|
| 叙事逻辑 | 核心 | 因果链、动机、信息揭示时机 |
| 人物一致性 | 核心 | 言行与设定匹配、角色声音区分 |
| 连贯性 | 标准 | 与前后章节衔接、时间线、位置 |
| 场景规划执行 | 标准 | 是否完成规划中的叙事任务 |
| 节奏与张力 | 标准 | 开头吸引力、节奏变化、张力曲线 |
| 对话质量 | 标准 | 功能性、潜台词、声音区分 |
| 描写质量 | 标准 | 感官体验、情绪外化、隐喻质量 |
| 去AI味 | 标准 | 自然度、个性、朗读测试 |
| 钩子与悬念 | 标准 | 开头钩子、结尾悬念、悬念管理 |
| 字数与密度 | 标准 | 字数达标、内容密度均匀 |

每个维度1-5分，满分50分。

| 结论 | 条件 |
|------|------|
| 通过 | ≥35分，且无单项≤2分 |
| 需修改 | 25-34分，或有单项≤2分 |
| 需重写 | <25分，或核心维度≤1分 |

## 技能包说明

技能包是子Agent的知识库，包含工作规范和参考技巧。

### 写作技能（writer-skill/）

| 文件 | 内容 |
|------|------|
| SKILL.md | 章节写作的完整流程和规范 |
| dialogue-writing.md | 对话标签规范、潜台词、语言指纹、信息倾倒规避 |
| description-craft.md | 感官层次、情绪外化、隐喻使用、密度控制 |
| content-expansion.md | 字数不足时的九种扩充策略 |

### 审查技能（reviewer-skill/）

| 文件 | 内容 |
|------|------|
| SKILL.md | 审查流程和输出规范 |
| review-checklist.md | 十维度审查清单和评分标准 |
| quality-standards.md | 每个维度的1-5分详细分级定义 |

### 润色技能（polisher-skill/）

| 文件 | 内容 |
|------|------|
| SKILL.md | 去AI味、对话修正、描写精炼、节奏微调、措辞优化、边界判断 |

### 规划与归档技能（planner-skill/）

| 文件 | 内容 |
|------|------|
| SKILL.md | 大纲构建、人物设计、世界观建立、场景规划、归档更新 |
| archive-maintenance.md | bible维护规范和格式标准 |
| templates/outline-template.md | 大纲模板 |
| templates/character-template.md | 人物档案模板（完整版/精简版） |

### 共享技能（shared/）

| 文件 | 内容 |
|------|------|
| hook-techniques.md | 开头钩子类型、结尾悬念类型、悬念管理 |
| deai-rules.md | 高频AI词汇、句式模式、风格模式、小说特有AI味 |

## 故事圣经（bible）

bible是整个项目的事实来源，由planner独占维护。

| 文件 | 内容 | 更新时机 |
|------|------|----------|
| characters/*.md | 人物档案（性格、语言指纹、当前状态） | 每章定稿后 |
| characters/relationships.md | 人物关系总览 | 关系变化时 |
| worldbuilding/ | 地理、规则、势力、时间线 | 新设定出现时 |
| plot/outline.md | 大纲、TODO、章节摘要、字数统计 | 每章定稿后 |
| plot/suspense-tracker.md | 悬念追踪（活跃/已回收） | 每章定稿后 |
| plot/foreshadow-tracker.md | 伏笔追踪（活跃/已回收） | 每章定稿后 |
| changelog.md | 所有更新的日志 | 每次更新时 |

## 设计原则

**为什么要分四个Agent？**
每个Agent有独立的上下文窗口，避免单一上下文过载。不同任务需要不同的思维模式（创作vs审查vs润色），职责边界清晰减少冲突和混乱。

**为什么用技能包而非系统提示词？**
技能包存储在文件中，可以版本控制和迭代。内容丰富时不占用对话上下文，子Agent按需读取而非一次性加载全部。

**为什么需要bible？**
长篇小说的角色、设定、悬念太多，无法靠记忆。文件化的bible让任何新会话都能恢复完整上下文，统一的事实来源避免前后矛盾。

**为什么每章都要审查？**
问题越早发现越容易修复。积累多章再审查会导致连锁修改，审查报告为润色提供精确的修改方向。

## 自定义与扩展

| 想要调整 | 修改文件 |
|----------|----------|
| 章节字数要求 | CLAUDE.md, writer-skill/SKILL.md, review-checklist.md |
| 审查维度和标准 | review-checklist.md, quality-standards.md |
| 去AI味规则 | shared/deai-rules.md |
| 添加写作技巧 | writer-skill/ 下添加文件，在SKILL.md中注册 |
| 人物档案字段 | planner-skill/templates/character-template.md |
| 大纲格式 | planner-skill/templates/outline-template.md |

## 已知限制

- 依赖Claude Code的Task工具实现多Agent协作
- 单章质量受模型能力限制，复杂场景可能需要多次重试
- 超长篇小说（50章以上）的bible可能变得庞大，需要定期精简
- 风格一致性在跨多个会话时可能出现波动
