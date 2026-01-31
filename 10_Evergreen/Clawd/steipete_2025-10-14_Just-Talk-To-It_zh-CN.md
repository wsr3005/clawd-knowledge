---
type: translation
author: Peter Steinberger (@steipete)
source: https://steipete.me/posts/just-talk-to-it
published: 2025-10-14
translated_at: 2026-01-31
note: "中文翻译；保留链接/术语；为可读性做了结构整理与少量意译"
---

# 《Just Talk To It：Agentic Engineering 的“不整虚的”方法》中文翻译

作者近来写得少，是因为埋头在做新项目。他认为“agentic engineering 已经强到几乎能写他 100% 的代码”，但同时也看到很多人把精力花在各种复杂的“仪式/表演”上，而不是把事做完。

这篇文章一部分来自他在伦敦的 Claude Code Anonymous 活动里听到的讨论，一部分来自于：距离他上次更新工作流已经过去“一整个人工智能年”，所以需要做一次复盘。

作者说明：基础理念仍然适用，所以他不再重复诸如“上下文管理”这种基础内容；如果你需要入门，可以先读他之前的《Optimal AI Workflow》文章。

---

## 1) 上下文与技术栈（Context & Tech-Stack）
作者是单人开发，当前项目规模很大：
- ~30 万行 TypeScript React 应用
- Chrome 扩展
- CLI
- Tauri 客户端
- Expo 移动端

托管在 Vercel：
- 一个 PR 大约 2 分钟就能部署出一个新版本网页用于测试
- 其他部分（app 等）并没有完全自动化

---

## 2) Harness 与总体方法（Harness & General Approach）
作者已经完全把 **codex CLI** 当作日常主力（daily driver）。

并行方式：
- 他通常在一个 3×3 的终端网格里同时跑 **3–8 个 codex**。
- 多数实例在同一个文件夹里（少数实验在别的文件夹）。
- 他试过 worktrees、PR 流程，但总会回到这个方式，因为“最快把事做完”。

### 2.1 原子提交（Atomic commits）
作者让 agents 自己做 git **原子提交**。
为了让 commit 历史尽量干净，他花很多时间迭代自己的 agent 配置文件，使得每个 agent 只提交它自己改过的文件，git 操作更“锋利”。

他也提到：
- Claude 有 hooks，但 codex 还不支持。
- 不过他认为模型很“聪明”，如果它铁了心要做某事，“没有哪个 hook 真能拦住它”。

---

## 3) 模型选择（Model Picker）
作者基本所有东西都用 **gpt-5-codex（中等设置）** 完成。
他认为这是“聪明与速度”的好平衡，并且它会自动调节思考强度。

作者的态度是：
- 不要过度纠结这些设置，因为通常没有显著收益。
- 少一个要操心的开关挺好（不用老想 ultrathink）。

---

## 4) “爆炸半径”（Blast Radius 💥）
作者说自己做任何改动都会先想“blast radius（影响半径/波及范围）”：
- 大概会改多少文件？
- 预计要多久？

你可以：
- 往代码库里扔很多“小炸弹”（小改动）
- 或者扔一个“大炸弹”（一次大改）再加几个小的

但如果同时扔多个“大炸弹”，会导致：
- 很难做隔离提交（isolated commits）
- 一旦出问题更难回滚

监控 agent 的方法：
- 如果一个任务比预期久，他会按 Esc 中断，问“现在进度怎么样（what’s the status）”，然后决定：帮它找方向 / 中止 / 继续。
- 他强调：不要害怕中途打断模型；文件变更是原子的，模型也很擅长从中断处继续。

不确定影响时的提示语：
- “在改之前先给我几个方案（give me a few options before making changes）”

---

## 5) 为什么不用 worktrees？
他通常只跑一个 dev server，然后边演进项目边在浏览器里点来点去，顺便同时验证多个变化。

如果每个改动都用一个独立 worktree/branch：
- 会慢很多
- 多个 dev server 也会很烦

另外他提到 Twitter OAuth 的限制：
- 回调域名能注册的数量有限，也限制了“多环境并行”。

---

## 6) 他为什么更喜欢 codex，而不是 Claude Code？
作者说自己以前很喜欢 Claude Code，但现在受不了它的一些“话术与姿态”（例如一堆“Absolutely right”以及测试失败时还说“100% production ready”）。

他觉得 codex 更像“内向但能扛活的工程师”：
- 开工前会读更多文件
- 所以很多时候你只给很短的提示，也能做得正中你想要的

他还列了一些 codex 的优势（原文要点）：
- 可用上下文更大（约 230k vs Claude 的 156k）
- token 更省：上下文涨得更慢
- 支持 message queue（排队消息）
- Rust 重写带来的速度/稳定性（少卡顿、少内存爆炸、无闪烁）
- “语言风格”更舒服，心理负担更低
- 不会到处生成随机 markdown 文件

---

## 7) 为什么不用各种“第三方 harness”？
作者认为：
- 用户和模型公司之间的“中间层空间”其实不大。
- 订阅制最划算：他现在有 4 个 OpenAI 订阅 + 1 个 Anthropic 订阅，总成本约 1000 美元/月，基本接近无限。
- 如果用 API 调用可能贵 5–10 倍（大概估算）。

他对 amp / Factory / Cursor 等做了很多吐槽与比较，总体结论是：
- 它们多是“薄封装”，长期护城河不明显。
- 这些工具终归会和大厂官方产品收敛。

他也提到：opencode / crush + 开源模型很有潜力，但目前还不够稳定。

---

## 8) Plan Mode 与“别演了，直接聊”
作者认为 benchmark 往往忽略了一个核心：模型+工具（harness）在接到 prompt 后“怎么制定策略”。

他觉得 codex 更谨慎：
- 会读更多 repo 文件再决定怎么做
- 会更强硬地拒绝不合理请求

因此他现在很少写“大 plan 文件”。

codex 虽然没有显式 plan mode，但他发现：
- 只要你写“我们先讨论（let’s discuss）”或“给我一些选项（give me options）”，它就会认真等待你确认。

结论就是标题那句话：
> 不需要一堆 harness 的表演。直接跟它聊。

---

## 9) 关于 Plugins / Subagents / 各种“花活”
作者对 Claude Code Plugins 非常不满，认为这像是在用“外挂/补丁”去修补模型效率问题。

他也批评了“subagents”这套叙事：
- 本质用例跟以前的 subtasks 差不多：并行、减少噪音上下文
- 他更喜欢自己开多个窗口，因为：
  - 对上下文工程的控制与可见性更强
  - subagent 返回什么、怎么返回更难 steer

他还吐槽 Anthropic 推荐的某些“AI Engineer agent”模板，认为那是缺少实质内容的“文字汤”，甚至可能是“上下文毒药”。

---

## 10) 他怎么写 prompt（How I write prompts）
作者说以前用 Claude 时，他会用很长的 prompt（也经常是语音口述）。

但换成 codex 后，他的 prompt 明显变短：
- 经常 1–2 句话 + 一张截图

他非常强调“截图”这个技巧：
- 模型能从截图里定位到具体字符串与页面元素
- 大约 50% 的 prompt 都会带截图
- 不一定需要标注，拖进终端就行

他仍然认为 Wispr Flow（带语义纠错）非常好用。

---

## 11) Web 版 agents
他最近又试了一圈 Devin / Cursor / Codex web。

他认为：
- Gemini 2.5 不太行了
- Jules 看起来不错但设置很烦
- 目前留下的是 codex web，但也有一些 bug

他把 codex web 当成“短期 issue tracker”：
- 在路上想到点子，用手机 iOS app 一句话记下来
- 回到 Mac 再统一 review

他也刻意不让自己在手机上做太多，因为担心工作更上瘾。

---

## 12) 背景任务（Background Tasks）与 tmux
他承认 codex 缺少一些 Claude 有的功能，最痛的是后台任务管理。
有时 codex 会卡在不会结束的任务（dev server、死锁测试）。

他的解决方案是：用 tmux。
- 模型对 tmux 有足够“世界知识”，你只要说“用 tmux 跑”，就不需要额外写复杂 agent 文档。

---

## 13) MCP：大多数应该是 CLI
作者认为大多数 MCP 更像“营销 KPI”，很多都应该用 CLI 替代。

他自己的论据：
- 你提一个 CLI 名字就够了；模型第一次会乱试，CLI 会吐 help，随后上下文就完整了。
- MCP 会持续吞上下文（context tax），CLI 基本没有。

他举例：
- GitHub MCP 可能直接吃掉 23k tokens
- 但 gh CLI 功能类似，模型天然会用，且不需要持续成本

他也承认自己写过多个 MCP，但现在更倾向于“CLI 优先”。

---

## 14) “代码会不会变成 slop？”
作者说他约 20% 的时间用在重构（当然也都让 agent 做）。
他列了一堆常见的重构/维护事项（原文要点）：
- 用 jscpd 查重复
- 用 knip 清死代码
- eslint 的 react-compiler / deprecation 插件
- 合并/整理 api routes
- 维护 docs
- 拆分过大的文件
- 加测试、加注释
- 升级依赖
- 重构慢测试
- 应用现代 React 模式（例如减少 useEffect）

他认为：
- “快速迭代”与“集中偿还技术债”这两种阶段切换，会更高产也更有趣。

---

## 15) Spec-driven development 还做吗？
作者说他过去会“写一个大 spec，让模型跑几个小时去实现”。
但他认为这是旧时代思路。

现在更常见的方式是：
- 先跟 codex 讨论
- 粘贴一些网站/想法/让它读代码
- 一起把 feature 讨论出来
- 如果很棘手，再让它把内容整理成 spec
- 然后拿给 GPT-5-Pro review，再把有用内容回填到主上下文

他还说：为 Sonnet 做“每次按 plan 新开上下文”可能有意义，但 GPT-5 在大上下文里能力更强；频繁重开上下文反而会拖慢节奏。

---

## 16) 他的 slash commands（很少）
他只保留少量命令，并且也不常用：
- `/commit`：强调多个 agent 同目录协作时只提交自己改的内容
- `/automerge`：按 PR 顺序处理，解决 bot 评论、跑绿 CI、最后 squash
- `/massageprs`：类似 automerge，但不 squash，方便大量 PR 时并行
- `/review`：内置命令，偶尔用

他强调：大多数时候直接打“commit”就行。

---

## 17) 一些“偷懒但好用”的小技巧
- 如果 codex 中途停了又你想离开：可以排队发几个 “continue”。
- 要求“每个 feature/fix 完成后写测试”，并且在同一上下文里写，质量会更好，也更容易发现 bug。
- 要求保留意图并在 tricky 部分加注释。
- 难题时加一些触发词：
  - “take your time”
  - “comprehensive”
  - “read all code that could be related”
  - “create possible hypothesis”

---

## 18) 他的 Agents 文件（提示词工程文件）长什么样？
他有一个 Agents.md（并用 symlink 兼容 claude.md），因为 Anthropic 没统一标准。

他指出：GPT-5 和 Claude 的“最佳提示风格”并不一致：
- Claude 可能对“全大写威胁式指令”反应好
- 但 GPT-5 会被这种风格干扰

所以他的建议是：
- 别吼，像人一样说话

他的 agent 文件大概 800 行，像“组织的疤痕组织（scar tissue）”：
- 不是他写的，是 codex 写的
- 每次出状况，他让 codex 追加一条简洁备注

内容通常包括：
- git 指令
- 产品说明、命名/API 偏好
- 新技术栈的世界知识补丁（比如更前沿的 React/Tailwind/React Compiler）
- 迁移管理、测试、ast-grep 规则等

---

## 19) GPT-5-Codex 完美吗？
作者说当然不：
- 有时会重构半小时然后“恐慌”回滚
- 有时忘了自己能跑 bash
- 偶尔莫名其妙用俄语/韩语回复
- 偶尔把 raw thinking 发给 bash

但这些都相对少见，他愿意接受。

他最大的烦恼：codex 会“丢行”，快速向上滚动时某些文本消失。

---

## 20) 结论（Conclusion）
作者的结论非常直接：
- 别把时间浪费在 RAG、subagents、Agents 2.0 等“表演/虚招”上。
- **直接跟模型对话，边用边玩，建立直觉。**

他引用了 Simon Willison 的观点：管理 agent 的很多能力，和管理工程师需要的能力很像；这些本身就是资深工程师的特质。

最后作者也强调：
- 写好软件依然很难。
- 即使不亲手写代码，他依然要做架构、系统设计、依赖选择、产品取舍。
- AI 只是把“交付预期”进一步提高了。

PS：作者说这篇文章是 100% 人工手写的（保持口吻与瑕疵）。

