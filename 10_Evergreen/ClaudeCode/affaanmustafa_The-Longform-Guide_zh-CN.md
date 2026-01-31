---
type: translation
author: affaanmustafa
source: https://x.com/affaanmustafa/status/2014040193557471352
fetched_via: https://r.jina.ai/
translated_at: 2026-01-31
note: "以下为中文翻译（保留代码块/命令原文；为可读性对少量重复/图片说明做了轻微整理）"
---

# 《Everything Claude Code：详细指南》中文翻译（Longform Guide）

## 0. 前置说明
作者说：在《精简指南》里讲的是“基础设施/配置搭建”（skills、hooks、subagents、MCP、plugins 等）。

这篇“详细指南”讲的是：**哪些技巧能把一次会话从‘浪费/上下文腐烂’变成‘长时间高效产出’**。

核心主题包括：
- Token 经济学（成本/上下文的管理）
- 记忆持久化（跨会话继续干活）
- 验证模式（verification patterns）
- 并行化策略
- 可复用工作流带来的复利

---

## 1. 跨会话记忆：用“会话日志文件”接力
作者建议：为了跨会话共享进度与状态，最好做一个 skill/command：
- 把当前进度做总结
- 写到 `.claude` 目录里的 `.tmp` 文件
- 会话结束前持续 append
- 第二天把这个文件作为上下文继续

注意点：
- **每次会话用新文件**，避免旧上下文污染新工作
- 最终会积累很多 session logs，需要备份或定期清理

作者说这些文件应包含：
- 哪些方法“确实有效”（最好有证据）
- 哪些方法尝试过但不行
- 哪些还没尝试
- 还剩什么待做

---

## 2. “战略性”清理上下文（Strategic Compact）
作者建议：
- 有了 plan 且探索阶段结束后，可以清掉无关的探索上下文，只按 plan 执行。
- 如果要更可控：关闭自动 compact，改为**在合适节点手动 compact**。
- 也可以做一个 hook：当工具调用累积到阈值时提醒你 `/compact`。

作者给了一个示例脚本（原文保留）：
```bash
#!/bin/bash
# Strategic Compact Suggester
# Runs on PreToolUse to suggest manual compaction at logical intervals
#
# Why manual over auto-compact:
# - Auto-compact happens at arbitrary points, often mid-task
# - Strategic compacting preserves context through logical phases
# - Compact after exploration, before execution
# - Compact after completing a milestone, before starting next

COUNTER_FILE="/tmp/claude-tool-count-$$"
THRESHOLD=${COMPACT_THRESHOLD:-50}

# Initialize or increment counter
if [ -f "$COUNTER_FILE" ]; then
  count=$(cat "$COUNTER_FILE")
  count=$((count + 1))
  echo "$count" > "$COUNTER_FILE"
else
  echo "1" > "$COUNTER_FILE"
  count=1
fi

# Suggest compact after threshold tool calls
if [ "$count" -eq "$THRESHOLD" ]; then
  echo "[StrategicCompact] $THRESHOLD tool calls reached - consider /compact if transitioning phases" >&2
fi
```

---

## 3. 高阶：动态注入系统提示词（System Prompt Injection）
作者提出一种模式：
- 不把所有内容都塞进 `.claude/rules/` 或用户级配置里“每次会话都加载”，
- 而是用 CLI 参数在启动时动态注入：

```bash
claude --system-prompt "$(cat memory.md)"
```

作者说明它相比“@文件引用”的差异在于：
- `@file` 或 `.claude/rules/` 多是通过工具读取（作为 tool output 进入对话）
- `--system-prompt` 是在对话开始前进入 **system prompt**，层级更高、权重更强

他建议做不同 alias：dev / review / research 模式切换：
```bash
alias claude-dev='claude --system-prompt "$(cat ~/.claude/contexts/dev.md)"'
alias claude-review='claude --system-prompt "$(cat ~/.claude/contexts/review.md)"'
alias claude-research='claude --system-prompt "$(cat ~/.claude/contexts/research.md)"'
```

作者也承认：很多情况下收益是“轻微优化”，不一定值得为所有人增加复杂度。

---

## 4. 高阶：记忆持久化 Hooks（生命周期钩子）
作者说有些 hooks 能显著改善“记忆”体验：
- PreCompact：压缩前保存关键状态
- Stop（session-end）：会话结束时持久化学习/总结
- SessionStart：新会话开始时自动加载近期上下文

示意（原文保留了一个流程图）：
- SessionStart 读取最近的 session files
- PreCompact 在压缩前写状态
- Stop 在会话结束时持久化到 `~/.claude/sessions/`

他给了 hooks 配置示例（原文保留）：
```json
{
  "hooks": {
    "PreCompact": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/memory-persistence/pre-compact.sh"
      }]
    }],
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/memory-persistence/session-start.sh"
      }]
    }],
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/memory-persistence/session-end.sh"
      }]
    }]
  }
}
```

作者观点：Stop hook 比 UserPromptSubmit 更合适做“学习总结”，因为：
- UserPromptSubmit 每条消息都会跑，开销大、增加延迟
- Stop 每次会话只跑一次，更轻量，也更容易对整段会话做整体总结

---

## 5. 持续学习（Continuous Learning）：把“别再犯同样错误”自动化
作者描述的问题：
- 重复提示、重复纠错会浪费 token/上下文/时间，体验也会让人烦躁。

解决方案：
- 当 Claude Code 发现“非平凡的知识”（debug 技巧、workaround、项目特定模式），把它保存为新 skill；下次遇到类似情况自动加载。

安装示例（原文保留）：
```bash
# Clone to skills folder
git clone https://github.com/affaan-m/everything-claude-code.git ~/.claude/skills/everything-claude-code

# Or just grab the continuous-learning skill
mkdir -p ~/.claude/skills/continuous-learning
curl -sL https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/skills/continuous-learning/evaluate-session.sh > ~/.claude/skills/continuous-learning/evaluate-session.sh
chmod +x ~/.claude/skills/continuous-learning/evaluate-session.sh
```

并在 Stop hook 里触发：
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/continuous-learning/evaluate-session.sh"
          }
        ]
      }
    ]
  }
}
```

另有 `/learn` 命令：不用等会话结束，遇到刚解决的难题可以立即提取成技能。

---

## 6. Token 优化：核心是“子代理架构 + 合适的模型分工”
作者的核心策略：
- 用子代理把任务分给“足够用但更便宜”的模型，减少浪费。
- 建议：
  - 90% 编码任务默认用 Sonnet
  - 失败一次/跨 5+ 文件/架构决策/安全关键时升级 Opus
  - 重复劳动/明确指令/当 worker 时降级 Haiku

他还提到一种更重的 benchmark 方法：
- 同一任务在不同 worktree 用不同模型跑一遍
- 用统一测试集/对比 diff 来评估

工具层面：
- 关注“最常被调用的工具”，例如用 mgrep 替换 grep/ripgrep，可能显著减少 token（作者声称平均可减半级别）。

后台进程：
- 能不把大量日志塞给 Claude 就别塞：用 tmux 跑后台，取你需要的片段再给 Claude。

---

## 7. 代码库模块化 = 省 token + 提一次成功率
作者观点：
- 模块化、可复用工具越多、单文件越短，Claude 读写越高效、重复读取越少。
- 巨型文件会导致多次 tool call、上下文丢失、重复读取成本更高。

---

## 8. 验证（Verification）与评估（Evals）
作者区分两种 eval 形态：
- **Checkpoint-based（检查点式）**：每到一个里程碑就按标准验证，不通过就修
- **Continuous（持续式）**：每 N 分钟或重大变更后跑测试/lint，发现回归立刻停下来修

Grader 类型：
- 代码型（字符串匹配/测试/静态分析）：快、便宜、客观但易脆
- 模型型（rubric 评分/自然语言断言）：灵活但不确定且更贵
- 人工：质量高但贵且慢

指标：
- pass@k：k 次尝试里至少 1 次成功（只要能跑通就行）
- pass^k：k 次都成功（强调一致性/确定性）

作者给了“构建 eval roadmap”的要点（意译）：
1) 尽早开始：从真实失败里拿 20–50 个任务
2) 把用户报错转成测试用例
3) 任务要足够明确：两个专家应得到同样结论
4) 平衡正/反例
5) harness 要稳：每次 trial 都从干净环境开始
6) 评估结果，不评估过程
7) 多读 transcripts
8) 如果 100% 通过就加难度（避免饱和）

---

## 9. 并行化：不要盲目追求“开很多终端”
作者反对“随意规定开多少个 Claude 实例”，认为应按需求扩展。

他建议的实践：
- main chat 专注实际代码改动
- forks 用于提问/研究/拉文档/找参考 repo
- 多实例改重叠代码时：必须用 git worktrees + 明确计划 + 用 `/rename` 给对话命名

并给了 worktree 示例（原文保留）：
```bash
git worktree add ../project-feature-a feature-a
git worktree add ../project-feature-b feature-b

cd ../project-feature-a && claude
```

他还提到“cascade method”：从左到右扫、一次只聚焦 3–4 个任务，避免心智开销超过收益。

---

## 10. 启动方式：双实例 Kickoff（作者偏好）
作者说自己常在空仓库里开两个 Claude：
- 实例 1（脚手架/搭建）：把项目结构、规则、agents、配置先搭起来
- 实例 2（深度研究）：连接服务、做 PRD、做架构图、拉文档引用

---

## 11. MCP 有时可用 CLI + skills 替代（省上下文/省 token）
作者观点：
- 很多 MCP 本质上是平台 CLI 的包装（GitHub/Supabase/Vercel/Railway…）
- 若 MCP 占上下文/成本高，可把常用操作做成命令/skills，用 CLI 执行

他也提到 Claude Code 团队在做 MCP 的 lazy loading，会缓解“上下文一开始就被吃掉”的问题，但 CLI + skills 仍可能在 token 成本上更优。

---

## 12. 作者收尾：想做一个端到端示例（视频/项目）
作者表示：可能会做一个端到端项目演示，把两篇文章的技巧串起来：
- 项目配置搭建
- token 优化
- verification loops
- 跨会话记忆管理
- 双实例 kickoff
- worktrees 并行

并列了一些参考资料（Anthropic evals、Claude Code best practices 等）。

