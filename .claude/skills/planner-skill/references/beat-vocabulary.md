# Beat 类型词典

> 用于场景规划中的 beat 级粒度设计。
> 每个 beat 描述"这个片段做什么"，不是"怎么写"。
> 给 writer 的是意图和方向，不是具体执行。

## 使用规则

- 每个场景由 1-4 个 beat 组成
- 标注"承重"的 beat 不可删除或调换顺序
- 标注"灵活"的 beat 可以合并、调整、用不同方式实现
- beat 是罗盘不是 GPS，writer 可以自由发挥实现方式

---

## 开场类 Beat

| 类型 | 做什么 | 适用场景 |
|------|--------|---------|
| Hook | 用反常/危机/悬念瞬间抓住注意力 | 章节开头、高潮场景开场 |
| Scene-setter | 建立时空、氛围、人物位置 | 新地点首次出现、节奏缓冲 |
| Callback Opener | 用上一章的钩子直接回应 | 承接悬念的章节开头 |
| In Medias Res | 从正在进行的行动中切入 | 紧张章节、战斗/对抗开场 |

## 行动类 Beat

| 类型 | 做什么 | 适用场景 |
|------|--------|---------|
| Confrontation | 两个立场冲突的直接碰撞 | 对抗、谈判、决裂 |
| Revelation | 关键信息被揭示 | 真相揭露、身份暴露 |
| Discovery | 角色主动发现新线索 | 调查、探索、试探 |
| Decision Point | 角色做出影响后续走向的选择 | 转折点、抉择时刻 |

## 紧张类 Beat

| 类型 | 做什么 | 适用场景 |
|------|--------|---------|
| Complication | 原本计划受阻，新障碍出现 | 行动受挫、局势恶化 |
| Counterattack | 角色反击，扭转被动 | 高潮前半段、绝地反击 |
| Steel-man Opposition | 让对立立场有说服力 | 辩论、理念冲突 |
| Tension Hold | 悬而不决，维持紧张 | 过渡中的紧张保持 |

## 情感类 Beat

| 类型 | 做什么 | 适用场景 |
|------|--------|---------|
| Breather | 短暂的喘息和放松 | 高强度场景之后 |
| Intensifier | 加深情感投入和共鸣 | 角色内心暴露、脆弱时刻 |
| Reflection Pause | 角色/读者消化刚发生的事 | 重大转折之后 |
| Empathy Moment | 让读者对角色产生共鸣 | 角色展示脆弱、善意、无奈 |

## 解决类 Beat

| 类型 | 做什么 | 适用场景 |
|------|--------|---------|
| Synthesis | 整合散落的线索和信息 | 揭秘章节、高潮收尾 |
| Resolution | 冲突有了明确结果 | 场景结尾、章节结尾 |
| Aha Moment | 角色或读者恍然大悟 | 伏笔回收、悬念解答 |
| Callback | 呼应前面的某个细节或台词 | 情感高潮、全书收束 |

## 过渡类 Beat

| 类型 | 做什么 | 适用场景 |
|------|--------|---------|
| Bridge | 连接两个功能不同的场景段 | 行动→情感、紧张→缓冲 |
| Cliffhanger | 在悬念点切断 | 章节结尾、场景切换 |
| Landing | 安全落地，给出确定感 | 紧张释放后、章节收束 |

---

## Beat 标注格式

在场景规划中使用：

    [Beat 1 - Hook - 承重]
    描述：[做什么，不是怎么写]

    [Beat 2 - Confrontation - 承重]
    描述：

    [Beat 3 - Breather - 灵活]
    描述：

## 承重 vs 灵活

- **承重**：此 beat 承载章节的叙事功能，删除或跳过会导致叙事断裂。writer 必须实现其意图，可以自由决定具体执行方式。
- **灵活**：此 beat 提供氛围或辅助信息，可以与其他 beat 合并、简化、或用不同方式实现。

## 常见 Beat 组合

| 章节类型 | 典型组合 |
|----------|---------|
| 开篇章 | Hook → Scene-setter → Confrontation → Cliffhanger |
| 推进章 | Callback Opener → Discovery → Complication → Decision Point → Cliffhanger |
| 高潮章 | In Medias Res → Confrontation → Revelation → Resolution |
| 缓冲章 | Breather → Reflection → Empathy Moment → Landing |
| 揭秘章 | Hook → Discovery → Synthesis → Aha Moment → Callback |
