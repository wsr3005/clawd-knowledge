---
type: translation
author: affaanmustafa
source: https://x.com/affaanmustafa/status/2012378465664745795
fetched_via: https://r.jina.ai/
translated_at: 2026-01-31
note: "以下为中文翻译（保留代码块/命令原文；为可读性对少量重复/图片说明做了轻微整理）"
---

# 《Everything Claude Code：精简指南》中文翻译（Shorthand Guide）

## 0. 背景
作者表示：这是他在 **10 个月高频日用 Claude Code** 后的完整配置与经验总结（skills、hooks、subagents、MCP、plugins 等），并提到自己使用 Claude Code 参与并赢得了 **Anthropic x Forum Ventures hackathon**。

---

## 1. Skills（技能）是什么？
- **Skills 很像“规则/工作流模板”**：它们通常作用在某个范围（scope）和固定流程（workflow）内。
- 你可以把 skill 当作“提示词的快捷方式”：当你要执行一个特定工作流时，直接调用 skill，而不是每次都从头写一大段提示。

作者举例：
- 长时间用 Opus 4.5 编码后想清理死代码、散落的 .md：可以跑 `/refactor-clean`
- 需要测试相关：`/tdd`、`/e2e`、`/test-coverage`
- **Skills 与 commands 可以在同一个 prompt 里串联调用（chaining）**。

作者还提到：可以做一个“检查点（checkpoint）更新 codemap”的 skill，让 Claude 更快理解代码结构，减少在探索阶段消耗上下文。

---

## 2. Commands（斜杠命令）是什么？与 Skills 的区别
作者的定义：
- **Commands 本质上也是技能**，只是以 **斜杠命令** 的形式被执行。
- 两者功能重叠，但存放位置不同：

```bash
# 示例
# Skills：更偏“宽泛的工作流定义”
~/.claude/skills

# Commands：更偏“快速可执行的一步/一组提示”
~/.claude/commands
```

---

## 3. Hooks（钩子）是什么？
作者的定义：
- **Hooks 是“基于触发器的自动化”**：在特定事件发生时自动执行。
- 与 skills 不同，hooks 往往绑定在 **工具调用（tool calls）** 或 **会话生命周期事件** 上。

作者列出的 Hook 类型：
1) PreToolUse：工具执行前（校验、提醒）
2) PostToolUse：工具执行后（格式化、反馈循环）
3) UserPromptSubmit：你发送消息时
4) Stop：Claude 完成回应时
5) PreCompact：上下文压缩前
6) Notification：权限请求

例子：在运行长耗时命令前提醒你用 tmux 保持会话：
```json
{
  "PreToolUse": [
    {
      "matcher": "tool == \"Bash\" && tool_input.command matches \"(npm|pnpm|yarn|cargo|pytest)\"",
      "hooks": [
        {
          "type": "command",
          "command": "if [ -z \"$TMUX\" ]; then echo '[Hook] Consider tmux for session persistence' >&2; fi"
        }
      ]
    }
  ]
}
```

作者建议：用 `hookify` 插件“对话式生成 hooks”，比手写 JSON 更快。

---

## 4. Subagents（子代理）是什么？
作者的定义：
- **Subagents 是主代理（orchestrator）可以委派的子进程/子角色**，它们有更小的任务范围（limited scope）。
- 子代理可以前台/后台运行，从而让主代理节省上下文、保持专注。
- 子代理可以结合 skills：把一部分 skills 授权给某个子代理，让它自主完成一类任务。
- 也可以给子代理更严格的工具权限（sandboxing / tool allowlist）。

示例结构：
```bash
~/.claude/agents/
  planner.md
  architect.md
  tdd-guide.md
  code-reviewer.md
  security-reviewer.md
  build-error-resolver.md
  e2e-runner.md
  refactor-cleaner.md
```

---

## 5. Rules（规则）怎么组织？
作者提到两种方式：
1) 单文件：所有规则写一个文件
2) rules 文件夹：把规则按主题拆分成多个 .md

示例：
```bash
~/.claude/rules/
  security.md
  coding-style.md
  testing.md
  git-workflow.md
  agents.md
  performance.md
```

作者给的“规则例子”（偏个人偏好 + 工程规范）：
- 代码库里不要 emoji
- 前端避免紫色系
- 部署前必须测试
- 优先模块化，不要巨型文件
- 不要提交 console.log

---

## 6. MCP（Model Context Protocol）是什么？
作者的观点：
- MCP 能让 Claude 直接连接外部服务（如 Supabase / DB / 部署平台等），是“prompt 驱动的封装”，更灵活。
- 但 **MCP 不是 API 的替代**，它更像“把 API/服务操作包装成对话可调用的能力”。

作者强调：**上下文窗口管理非常关键**
- MCP/工具启用太多，会显著压缩你可用上下文，导致性能下降。
- 经验法则：
  - 配置里可以有 20–30 个 MCP
  - 但每个项目实际启用最好 < 10 个，或总 tools 数 < 80（作者给的“粗规则”）

作者也提到：Claude 内置的 Chrome / Browser 控制（作为 MCP/插件能力）可以让 Claude 自动操作浏览器。

---

## 7. Plugins（插件）是什么？
作者的观点：
- Plugins 用来“打包安装”工具/skills/hooks/MCP，省去手动配置。
- LSP 插件在不用 IDE 的时候很有价值：提供类型检查、跳转定义、补全等。
- 但同样要注意：插件/MCP 太多会挤占上下文。

作者举例（启用插件示意）：
```bash
typescript-lsp@claude-plugins-official
pyright-lsp@claude-plugins-official
hookify@claude-plugins-official
mgrep@Mixedbread-Grep
```

---

## 8. 并行工作流建议
作者建议的并行方式包括：
- `/fork`：把对话分叉并行做不重叠的事情
- **Git worktrees**：为多个 Claude 实例创建独立工作树，避免冲突

```bash
git worktree add ../feature-branch feature-branch
# 在不同 worktree 里跑不同 Claude 实例
```

- **tmux**：用于长运行命令/日志监控，避免在 Claude 的上下文里滚太多输出

---

## 9. 终端/编辑器的配合
作者观点：编辑器不是必须，但能影响体验。
- 作者偏好：Zed（轻量、快，和 Claude 集成好）
- VSCode / Cursor 也可用。

---

## 10. 作者的“最终提醒/原则”
作者在文末给出一些原则（意译整理）：
1) 别过度复杂化：把配置当成“微调”，不是重新造系统
2) 上下文窗口很宝贵：禁用不需要的 MCP/插件
3) 并行要有章法：fork + worktrees
4) 重复性工作尽量自动化：用 hooks 做格式化、lint、提醒
5) 子代理要严格限权：工具越少越聚焦

