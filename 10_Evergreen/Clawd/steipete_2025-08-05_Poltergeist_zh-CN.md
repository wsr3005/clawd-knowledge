---
type: translation
author: Peter Steinberger (@steipete)
source: https://steipete.me/posts/2025/poltergeist-ghost-keeps-builds-fresh
published: 2025-08-05
translated_at: 2026-01-31
note: "中文翻译；保留链接/命令；为可读性做了小标题整理与少量意译"
---

# 《Poltergeist：让构建永远保持新鲜的幽灵》中文翻译

**TL;DR：**[Poltergeist](http://polter.build) 是一个对 AI 友好的“通用文件监听器（file-watcher）”。它能自动识别项目类型，一旦文件变化就自动触发重建（rebuild），并带通知与智能构建队列。

作者的类比：它像是“给原生应用的 npm run dev”，零配置、自动化。

---

## 1) 故事（The Story）：迭代速度决定一切
在作者口中的“agentic engineering”里，**迭代循环（code→build→test→debug）的速度**就是一切。

作者在做 Peekaboo（Swift 写的 macOS 自动化 agent/cli/mcp）时，最大的摩擦来自构建时间：
- Swift 编译不快
- 当 Swift 还在算依赖时，TypeScript 项目都已经重编完了

更糟的是：agent 有时会忘记在测试前重建，导致你在“其实已经修复了”的代码上 debug。

Poltergeist 的核心价值：
- 文件一改就后台自动构建
- 人和 agent 的 code/debug loop 都更快

作者最初只写了一个 bash 脚本监听 Swift 文件并自动构建，解决了 Swift 项目。
但他很快意识到：这对任何项目都很有用，于是决定做成一个通用工具。

---

## 2) 通用方案（The Universal Solution）
作者把整个系统用 TypeScript 重写，目标只有一个：
- 适配任何项目、任何语言、任何构建系统。

Poltergeist 变成了一个“会闹鬼”的通用 watcher。

作者提到：类似 watchexec 的工具虽然存在，但没有一个是面向 agentic engineering 的工作流设计的。

Poltergeist 甚至会检测“调用者是人还是 agent”，并在输出里给 agent 更多引导信息，避免污染你的 AGENTS.md。

体验上：
- 一切尽量“不可见”地发生：你保存文件，等你准备测试时，最新二进制已经在那了。
- 对 Mac app，甚至可以自动退出并重启（当然可配置）。
- 真正的 hot reload 会更好，但留给未来。

---

## 3) 用 Claude Code “召唤幽灵”（Channeling the Spirit）
作者说：Poltergeist 完全是用 Claude Code 构建的。

项目起初只是 bash 脚本；后来他让 agent 把它们转换成 TypeScript，然后不断迭代。

他认为“全是自动生成代码”这类说法已经没意义：
- 他为了把设计磨好，写/说了大量 prompt（“20 页英语”）
- 在 AI 时代，英语正在变成新的编程语言；TypeScript 只是实现细节

为什么选 TypeScript：
- agent 写 TS 非常稳
- 迭代快，编译几乎瞬时
- 跨平台
- Watchman 有 TS bindings

---

## 4) 与 agent 共舞（Dancing with Agents）：提示与流程
作者很喜欢做开发者工具。

他提到自己通常用 spec.md 的方法开启新项目，但 Poltergeist 是从脚本自然演化成工具的，所以没有正式 spec，主要靠大量 prompt + 迭代。

他的一些经验：
- agent 很擅长 TS 和 Go，很多 prompt 能 one-shot
- 他用 WisprFlow 口述，prompt 往往很长很散
- “多说一点、解释你为什么要这样”会显著提升 agent 理解与实现质量

常用提示套路：
- “长 prompt + plan only ultrathink”
- 不确定时让 agent 给几个 options
- 他不太用 Claude 的 plan mode，直接说“plan only”更贴合自己的 flow
- 经常在 plan 上迭代几轮，确认后再输入 “y” 让它动手做

做完主功能后，他常写：
- “add tests + update docs”

理由：
- 有上下文时写测试最容易发现 bug，也最容易顺手修。
- 每个 feature 写一小段测试比最后补全更靠谱。

他还会尽早加 CI（GitHub Actions），确保跨 OS 不只是本机能跑。

---

## 5) 一次“转 Go”的实验：Poltergohst
作者在写博客时问 Claude 对语言选择的看法，得到意外答案。
于是他让 agent loop 几小时把项目改写成 Go（作为实验）。

他提到开源模型/替代 CLI（OpenCode/Crush + Qwen/GLM）目前坑还很多，不推荐。

他把转换过程做了一个技巧：
- 把重要源码/测试等转换成一个 1.1MB 的 markdown
- 再整体复制粘贴并下指令“convert to Go”
- 绕过 256KB 限制导致的“只读部分文件/读得很慢”问题

他还推荐一个把 GitHub repo 转文本的网站（可选文件类型，快）：
https://repo2txt.simplebasedomain.com

最终他放弃 Go 的原因：
- 自己对 Go 不够舒服
- Bun 的 SPA mode 启动很快（~44ms），适合 Homebrew 分发单二进制
- 生态：Poltergeist 依赖 Watchman，TS bindings 很好，但 Go binding 生态弱且维护差

实验项目保留在 GitHub：
- poltergohst：https://github.com/steipete/poltergohst

---

## 6) 如何使用（Seance Time）
作者建议：现代 Mac 用 homebrew，其它平台用 npm。

```bash
# For modern macOS
brew tap steipete/tap
brew install poltergeist

# Windows, Linux, Intel Mac (Node 20+)
npm install -g @steipete/poltergeist

# Auto-detect and configure your project
poltergeist init

# Start watching & rebuilding
poltergeist haunt

# Run your tool (always fresh!)
polter my-cli --help
```

他还提到有一个原生 macOS 菜单栏 app（尚未正式发布），源码可看。

---

## 7) 结尾：最好的工具是“隐形”的
作者总结：Poltergeist 是一种面向“人 + agent”的新型工具。
你装一次就可以忘掉它：它在后台默默工作，但当你需要时又会变得不可或缺。

“最好的工具在你不需要时是隐形的，一旦拥有就不可替代。Poltergeist 就是这样——而它只需要一次 init。”
