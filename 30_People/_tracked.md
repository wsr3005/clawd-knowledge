---
type: list
name: tracked_people
updated: 2026-07-16
---

# Tracked People（09:00 个人源采集名单）

> 只做候选素材采集，不直接生成或推送日报。
> 09:10 战略雷达负责最终判断、精选入库和用户推送。
> 权威/官方/核心 builder 名单由 `~/.hermes/scripts/ai_authority_accounts.json` 维护，避免重复管理。

## Handles

- @vista8
- @op7418
- @YukerX
- @sodawhite_dev
- @fmdz387
- @servasyy_ai
- @Khazix0918
- @akokoi1
- @mike_chong_zh
- @MiniMax_AI
- @binghe
- @dotey

## 已移除/暂停

- `@lyc_zh`：账号失效，2026-07-16 移除。
- `@AppSaildotDEV`：账号失效；疑似改名为 `@app_sail`，但不属于当前 AI/Agent 主战场。
- `@lidangzzz`：近期泛教育/情绪内容持续污染 AI/Agent 候选，暂停采集。
- `@lxfater`：近期低信息量互动内容较多，暂停采集。
- `@elonmusk`：不进入每日 AI/Agent 采集。

## 采集约束

- 每个账号抓取最近 10 条，仅保留过去 48 小时的候选。
- 原始内容写入 `.daily_fetch/YYYY-MM-DD/candidate_pack.json`。
- 每日 following 快照写入 `.daily_following/YYYY-MM-DD.json`，只用于识别关注变化。
- 原始素材不直接进入 `00_Inbox`，也不直接提交 Git。
