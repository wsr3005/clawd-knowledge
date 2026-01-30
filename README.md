# clawd-knowledge

一个用纯 Markdown 维护的个人知识库（也可直接作为 Obsidian Vault 打开）。

## 目录约定
- `00_Inbox/`：每日/每次采集的精选（先收集，后提炼）
- `10_Evergreen/`：常青知识卡片（框架、方法论、可复用结论）
- `20_Trends/`：趋势周报（每周一篇）
- `30_People/`：信息源画像（值得关注的人）
- `assets/`：附件（可选）

## 入库模板
### Inbox 帖子卡
```md
---
type: x_post
date: YYYY-MM-DD
topic: [agents, skills]
source: https://x.com/.../status/...
author: "@handle"
signal: [经验, 观点, 趋势]
---

一句话结论：

摘要（3-5 行）：

我能立刻用上的点（可空）：

关联人物/账号：
```

### Evergreen 常青卡
```md
---
type: evergreen
topic: 信息源筛选
updated: YYYY-MM-DD
---

结论（1-2 句）：

适用范围/边界：

证据/来源：
- 

我的默认做法：
1)
2)
```

### People 画像卡
```md
---
type: person
handle: "@handle"
focus: [agent, security]
follow_status: candidate
---

为什么值得关注：
- 

代表帖：
- https://x.com/... （一句话）
```
