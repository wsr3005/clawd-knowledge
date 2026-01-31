---
type: translation
author: Peter Steinberger (@steipete)
source: https://steipete.me/posts/2025/signature-flicker
published: 2025-12-17
translated_at: 2026-01-31
note: "中文翻译；保留链接/代码；为可读性少量意译与小标题整理"
---

# 《标志性的闪烁（Signature Flicker）》中文翻译

**tl;dr：**“地狱结冰了”。Anthropic 在最新更新（2.0.72）里修复了 Claude Code 里那个标志性的 UI 闪烁问题。

如果说大家对 Claude Code 除了“它正在改变我们写软件的方式”之外最一致的记忆是什么，那就是——**闪烁**。这也不完全是 Anthropic 的锅：像 Cursor 这类 TUI，或者任何基于 [Ink](https://github.com/vadimdemedes/ink) 的东西，也会遇到类似问题。这个问题并不简单，因为 Claude Code 在底层用的是 React。

## 问题是什么？
终端（Terminal）从设计之初就不是为了高度交互而生的。

你当然可以用 [ANSI 转义码](https://en.wikipedia.org/wiki/ANSI_escape_code) 去移动光标、覆盖写入，但如果更新策略做得不好，就会出现闪烁。

大体有两条路：

1) 进入 **alt screen / alternate screen mode（替代屏幕）**：让应用完全接管终端视口。

2) 保持主屏幕缓冲区（primary buffer），**只增量重绘发生变化的部分**，尽量不破坏 scrollback。

两者都不完美，各有取舍。Mario Zechner 在他关于 pi-coding-agent 的文章里把细节讲得很好（作者在此不复述）。作者自己也做过第 2 种方案：他把 pi-tui 从 Swift 生态迁移成了 [TauTUI](https://github.com/steipete/TauTUI)（大部分自动翻译由 Codex 完成）。

对于“主要输出是文本、交互相对有限”的 coding agent，作者认为：**在保持良好终端公民（terminal citizen）的前提下，仅增量重绘变化部分**，通常是更好的选择。

Anthropic 看起来也同意。

Claude Code 最初使用的 React 终端渲染器 Ink，并不支持 long-running interactive UI 需要的那种“细粒度增量更新”。虽然 Ink 上游后来有改进（作者引用了 PR），但 Anthropic 需要更强的控制力，于是他们 **从零重写了渲染器**，但依然保留 React 作为组件模型。

作者引用 Anthropic 的 Thariq：
> 这有点像网站自己实现文本渲染、高亮、鼠标移动、右键菜单……它就不会像浏览器。我们非常重视这种原生体验。未来可能探索 alt screen，但我们的门槛很高。

## 生态现状（Landscape）
过去一年里，大多数新的 coding agent 最终都走向了 alt-screen TUI（很多也是被闪烁逼的），但体验往往不太好。

作者对 alt mode 最大的不满：它会破坏终端原生能力，比如：
- 选中文本的体验
- 原生滚动（native scrolling）
- 原生搜索（search）

当然这些功能也能在 TUI 内重做，但总觉得“不像终端了”。

### Amp
Amp 早期也用 Ink（同样闪烁），后来自己写渲染器并在 9 月切到 alt mode。
但问题包括：
- find 只能在当前屏幕可见文本里工作
- 选择/右键菜单体验不够原生
- 自己实现滚动条，能用但不像终端

### Gemini
Google 曾在博客高调发布新的 alt-mode TUI，但用户非常不喜欢，甚至不到一周就回滚。
在那套 TUI 里，复制文本需要按 **CTRL-S** 进入选择模式。

### OpenCode
OpenCode 做了很强的工程实现：用 TypeScript + Zig 构建了 [opentui](https://github.com/sst/opentui)，可渲染 SolidJS/React。
但也有问题：
- 在 macOS 26 以下的系统自带 Terminal、以及 GNOME Terminal 上不工作（作者引用 issue）
- 边缘自动滚动对小屏很痛苦
- 没有滚动条；搜索也不符合预期
- 右键→粘贴到输入框不工作

### Codex
作者对比 OpenAI 的 Codex：它依然留在 primary buffer，和终端交互方式符合预期。

Codex 也不完美（有时会覆盖文本行），但它做对了最关键的一点：**它像一个终端那样工作**。
所以作者认为 Codex 现在朝 alt-mode TUI 的方向走，像是倒退而不是升级（希望他们回头）。

### pi
Mario Zechner 的 [pi](https://shittycodingagent.ai/) 是“差分渲染”的当前标杆，还能使用现代终端的各种能力（甚至内联图片）。

## 结论（Verdict）
Claude Code 和 pi 证明：你可以消除闪烁，同时不牺牲终端的“肌肉记忆”。

alt mode 对仪表盘很棒；但对 coding agent，作者更希望保持终端原生能力：
- 像终端一样选中文本
- 像终端一样 scrollback
- 像终端一样搜索

现在是 2025：我们可以同时拥有丝滑渲染和终端的超能力。

---

*脚注：作者补充自己第一次听说 Claude Code 用 React 时也觉得很怪，但也很美——React 的概念足够灵活，不一定需要浏览器作为前端。*
