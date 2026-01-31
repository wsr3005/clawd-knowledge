---
type: translation
author: Peter Steinberger (@steipete)
source: https://steipete.me/posts/2025/live-coding-session-building-arena
published: 2025-09-06
translated_at: 2026-01-31
note: "中文翻译；保留链接/要点；为可读性对 AI-assisted summary 做了结构化整理"
---

# 《直播写代码：构建 Arena》中文翻译

**tl;dr：**作者用一场约 1 小时的直播，现场完成并上线了一个全新功能，展示自己如何用 codex 做 agentic engineering。

作者邀请你看一场“无滤镜”的 live coding：不写稿、真实呈现开发过程。他感谢 Eleanor Berger 促成这次视频与活动。

视频（YouTube）：
https://www.youtube.com/watch?v=68BS5GCRcBo

## 我们构建了什么？（作者原文标注：AI-Assisted summary）
- 功能：Arena —— 作者某个即将发布项目里的新功能，用于判断 X 上 2–4 个用户“匹配度”如何。
- 输入：Twitter/X 用户 handle
- 流水线：
  - 每个用户抓取 N 条推文（总预算 1000 条）
  - 只保留必要字段
  - 做 profile analysis
  - 计算兼容性分数（两两 pair + 全队 team）
- 体验：
  - 用户选择器 + “Analyze”按钮
  - 结果表格
  - 搜索框下方可选历史缓存结果（cached runs）
- 基建：
  - arena_cache 的 DB migration
  - 后台长任务（long-running job）
  - streaming UI
  - 鉴权保护页面

作者说自己大约 1 小时完成了功能，并且他和 @intellectronica 的 pair score 是 89。

## 技术栈 & 设置
- 模型工作流：作者用 codex（OpenAI/GPT-5）作为主要 coding agent。
  - 体验：codex 会更主动地读代码库，不需要你手把手列文件清单；很多时候“会自己做对”。
  - 他也会用 Claude 风格做一些 web search，但 repo 内开发 codex 更强。

- 会话习惯：
  - 大功能尽量开新会话
  - 多开几个 agent 窗口并行；当一个在思考时切别的任务

- 分支策略：
  - 直接在 main 上开发
  - 用“原子提交（atomic commits）”保持安全
  - 作者认为 worktrees/merge conflicts 会拖慢速度；小而清晰的提交可以兼顾速度与安全

- 工具：
  - Ghostty：多分屏终端
  - Better Stack logging：用一个很小的 [bslog](https://github.com/steipete/bslog) CLI
  - 自己写了 xl CLI（curl wrapper）快速拉 X API
  - 严格 biome 规则 + 自定义 codemods 规范输出
  - 后台 worker：用 [Inngest](https://www.inngest.com/)
  - 缓存表：避免重复计算
  - 文档摄取：只拉需要的部分；优先 markdown（爬虫转换）而不是原始 HTML，以节省 token
  - 校验：对输入做 schema validation；尽早失败并给出清晰错误

## 关键战术（作者认为最重要的点）
- **保持上下文干净**：减少工具噪音；只有必要时才注入 docs；markdown > HTML
- **让 codex 按需规划**：它给的下一步通常很靠谱，你逐步放行即可
- **尽早加缓存**：在 UI 打磨前先把“耗时任务的缓存表 + 后台队列”搞定，避免贵的分析反复跑
- **错误日志原样粘贴**：不要过度解释，直接把 logs 扔进去让 agent 修
- **把注释当规格（spec）**：在 tricky code 附近要求写清晰意图注释，方便你和下次会话的 agent
- **测试可以后补**：先把形态做出来，再让 agent 回填测试，通常足够避免回归
- **main 上开发 + 精细提交**：快但不鲁莽；Git + 备份是安全网
- **别用本地模型做这种工作负载**：上下文与稳定性更重要
- **CLI 胜过 MCP**：两小时写个 CLI wrapper（日志、API 拉取）很快回本，还能保持上下文更小
- **用小 proof 项目打通难点**：比如 streaming/protocol 难，就先在仓库里做个小可运行 demo，再移植回主功能

## Q&A 精华
- 为什么 Codex > Claude Code？
  - 作者感受：codex 会更主动读 repo、更少“看这里看那里”的手把手引导；Claude 仍适合搜索/网页，但 coding 端到端 codex 更快。

- 会开分支吗？
  - 现阶段不做。main + 纪律性提交更快，也（反直觉地）更安全。

- agent 的手动审批？
  - 作者不做，因为会变成“Windows Vista 弹窗”。更好的方式：Git + 备份 + diff review。

- repo prompt / MCP servers？
  - 作者觉得会膨胀上下文并引入脆弱性；更偏好“精简指令 + 小 CLI”。

- compaction & 长会话？
  - 尽量把 feature 规划到上下文能装下的范围；如果预期很多循环（比如修测试），用更擅长 compact 的工作流，或拆任务。

文末作者还推荐：
- 他自己的 AI 开发工作流文章：/posts/2025/optimal-ai-development-workflow
- OpenAI GPT-5 Prompting Guide：https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide
