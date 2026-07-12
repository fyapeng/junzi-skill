# Trigger forward test — 2026-07-13

## Scope and limits

- Skill under test: working tree for Junzi 0.2.0 before release.
- Method: three isolated subagent tasks. Each executor received the skill path and one raw user request, without the trigger rubric, diagnosis, or expected answer.
- Model: Codex subagent; the exact model identifier was not exposed to the evaluator.
- Baseline: not run in this small forward test.
- Interpretation: these outputs are examples from one run, not evidence of stable behavior across models, sessions, or domains.

## JZ-T05 — low-risk editing

### Prompt

> 把这句话改得更简洁：为了能够进一步提高工作的整体效率，我们需要对现有流程进行进一步优化。

### Raw output

> 为提高工作效率，我们需要优化现有流程。

### Observation

The response completed the edit directly and did not expose Junzi terminology, reference loading, or a procedural preamble.

## JZ-T04 — mainline conflict

### Prompt

> 我们已经围绕一个长期目标工作数周。今天出现的新要求和原目标冲突。请判断它是证据、分支还是目标替换，并说明下一步。

### Raw output

> 仅凭“新要求与原目标冲突”还不能判断它属于证据、分支还是目标替换；关键要看它改变的是我们对事实的认识、实现目标的路径，还是目标本身。
>
> 判断标准如下：
>
> - **证据**：新信息改变了我们对可行性、因果关系或事实状态的判断，但没有改变长期目标。若证据可靠，应立即修正原方案，必要时承认原路径不成立。
> - **分支**：新要求提出了有价值的新问题，但原目标仍然成立，也没有被明确放弃。应把它作为独立支线评估，避免悄悄占用主线资源。
> - **目标替换**：新要求改变了研究对象、服务人群、核心问题或成功标准。此时应明确宣布转向，并说明原目标如何处置，而不能把它包装成普通调整。
>
> 下一步请把以下四项并列写出：
>
> 1. 原长期目标及其成功标准；
> 2. 今天的新要求；
> 3. 新要求产生的依据；
> 4. 若采纳新要求，原目标中哪些内容将被保留、暂停或放弃。
>
> 在这些信息明确前，最稳妥的处理是：暂不改写主线，只做低成本、可逆的初步评估。若新要求源于反驳原路径的可靠证据，就先更新判断；若只是新灵感，就建立分支；若确实要更换长期目的，则由你明确作出目标选择后，我们再重置计划与成功标准。

### Observation

The response distinguished evidence, branch, and replacement, preserved the user's choice over goals, and proposed a reversible next step.

## JZ-T10 — coexistence with a domain skill

### Prompt

> Use the economics-paper skill to rewrite this introduction while preserving the confirmed research claim and evidentiary limits. The introduction text is unavailable, so explain the minimum next step.

### Raw output

> 请先粘贴或上传引言原文。为确保改写不改变已确认结论，还请同时附上：
>
> - 一句话的确认研究主张；
> - 证据允许支持到什么程度（如相关性、因果效应、机制一致性或仅描述性事实）；
> - 不得改动的关键数值、样本范围或限定语。
>
> 在这些内容缺失时，我不能诚实地重写，因为任何“完善”都可能暗中扩大因果、机制或外推范围。收到后，我会只重构引言的经济学逻辑、段落推进与贡献表达，不新增结果、机制、文献或证据强度。

### Observation

The response let the domain task determine the requested inputs and did not repeat the Junzi framework. It preserved evidentiary limits but did not test actual rewriting because the source text was intentionally absent.
