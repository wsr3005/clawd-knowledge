---
type: translation
author: Peter Steinberger (@steipete)
source: https://steipete.me/posts/2025/optimal-ai-development-workflow
published: 2025-08-25
translated_at: 2026-01-31
note: "中文翻译；保留链接；为可读性做了小标题整理与少量意译"
---

# 《我当前的 AI 开发工作流（My Current AI Dev Workflow）》中文翻译

**TL;DR：**Ghostty + Claude Code + 极简工具链 = 最高生产力。作者的理念是“少即是多”。

作者表示：是时候更新一下他的工作流了（它一直在变化）。

他曾一度全面转向 VS Code，但现在又把主力环境切回 [Ghostty](https://ghostty.org/)：
- 主力：Ghostty（终端）
- 辅助：VS Code（用来查代码）
- 评审（review）：Cursor/GPT-5（有时也用 CLI）
- 也试过 Zed，但不喜欢它的终端观感。

硬件上，作者很满意自己的 40 寸 Dell UltraSharp U4025QW（3840×1620）：
- 能同时看 4 个 Claude 实例 + Chrome，无需移动窗口。

作者吐槽：VS Code 的 terminal 不稳定，粘贴大量文本时会 freeze；Ghostty 更稳。

---

## 1) 工具与现实（Tools and Their Reality）
- Gemini 有时很好用，但它的 edit 工具太“乱”，所以作者用得越来越少。
- 用 GPT-5 来 review 计划（plan）甚至比 Gemini 更好。

并行方面：
- 所有工具都可以直接在 main 上用。
- 他试过 worktree 的方案，但觉得会拖慢自己。
- 如果选好工作区域，可以在同一个 main 上并行处理多个模块，互相污染不大。

作者对 Claude 的评价：
- Claude 有时会把东西弄乱，但它同样很擅长重构和清理。
- **重要的是：重构/清理要和开发同时进行**，否则很容易积累技术债。

---

## 2) 规划与上下文管理（Planning and Context Management）
作者觉得很有用的一点：
- 在 statusline 里显示“初始主题 + session id”，这样如果要切账号或重启 session，会非常方便（他还给了 gist）。

做事方式：
- 关键是用 plan mode 并反复迭代。
- 小任务直接做；大任务写到文件里，然后让 GPT-5 review。
- 很多时候作者只用很短的 prompt 就能推进；有时会脑暴、表达很散，但 agent 也能从“混乱思路”里提炼出可执行方案。

并行数量：
- 不重构时一般跑 1–2 个 agent。
- 清理/测试/UI 工作时 4 个左右是“甜蜜点”。
- 取决于任务的 blast radius（影响面）。

---

## 3) 难点（The Hard Parts）
作者认为最难的是：
- 分布式系统设计
- 选对依赖与平台
- 设计有前瞻性的数据库 schema

他提到自己建了很多“自定义基础设施”：
- 管理后台页面
- 各种 CLI（既帮自己也帮 agents）

这些事情让他速度提升巨大——如果按旧时代方式他根本不会去做这些工具。

---

## 4) 测试策略（Testing Strategy）
- 大改动一定要有测试。
- 自动生成的测试“通常不太好”，但如果你让模型在 **同一上下文** 里写测试，它几乎总能发现问题。
- 作者强调：上下文很宝贵，不要浪费。

---

## 5) 少即是多（Less is More）
作者甚至把最后一个 MCP 也移除了：
- 因为 Claude 有时会在不需要时自作主张启动 Playwright。
- 其实直接读代码更快、而且对上下文污染更小。

服务选择偏好：
- 选那些有 CLI 的服务：vercel、psql、gh、axiom。
- 在 CLAUDE.md 里写一行提示就够：
  - “日志：axiom 或 vercel cli”
  - “数据库：psql + 一个如何正确加载 env 的示例，让循环更快”

---

## 6) 对比与结论（Results and Comparisons）
作者认为：用这套配置，他做成了“离谱多”的事情。

但他也指出其他工具的不足：
- Codex 不擅长搜索（在很多情况下直接“google best practices”更好）。
- Cursor/GPT-5 很慢，而且不展示思考过程，不好 steer。
- GPT-5 更“字面”，要更精确具体地 prompt；它是很好的模型，但不算最好的 agent。

最后作者说：
- 他不太能想象把这套流程完全交给后台 agents。
- 因为他会在过程中不断观察 drift 并手动校正；后台运行更难做到。

作者还提到：新 rate limits 将在 8 月 28 生效，会很难受；目前似乎只能付费，没有完美替代品。
