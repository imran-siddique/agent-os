# SCAK Demo Video Script (2-3 Minutes)

**Target Length:** 2:30  
**Format:** Screen recording with voiceover  
**Tools:** OBS Studio + simple video editor

---

## Opening (0:00 - 0:15)

**[SCREEN: GitHub repo README]**

**Voiceover:**
"The Self-Correcting Agent Kernel - or SCAK - is an open-source framework that teaches AI agents to learn from their failures automatically. Let me show you why this matters."

---

## Problem Statement (0:15 - 0:45)

**[SCREEN: Terminal showing standard agent failing]**

```bash
$ python demo/standard_agent.py
User: Find the Q3 report
Agent: I couldn't find any Q3 report.
❌ FAILED - Data actually exists in archive/2025-Q3-Final.pdf
```

**Voiceover:**
"AI agents get lazy. They give up with 'I couldn't find that' even when data exists. This happens because they use low reasoning effort - not because the task is impossible.

The standard fix? Keep adding instructions to the prompt. But this causes unbounded growth - eventually, your context window explodes and performance degrades."

---

## Solution Part 1: Differential Auditing (0:45 - 1:15)

**[SCREEN: Terminal showing SCAK agent with auditing]**

```bash
$ python demo/scak_agent.py
User: Find the Q3 report
Agent: I couldn't find any Q3 report.

🔍 Differential Auditing triggered (give-up signal detected)
👨‍🏫 Shadow Teacher (o1-preview) verifying...
✅ Teacher found: archive/2025-Q3-Final.pdf
📝 Generating competence patch...
✅ Patch applied

Retry:
Agent: Found Q3 report at archive/2025-Q3-Final.pdf
✅ SUCCESS
```

**Voiceover:**
"SCAK catches this with Differential Auditing. When an agent gives up, we verify with a stronger teacher model - like o1-preview. If the teacher finds data, we know the agent was lazy.

Then we generate a competence patch - a specific instruction that prevents this failure in the future. Our experiments show a 72% correction rate."

---

## Solution Part 2: Semantic Purge (1:15 - 1:45)

**[SCREEN: Visualization of context growth]**

**Animation showing:**
1. Context growing with patches
2. Model upgrade triggering purge
3. Type A patches deleted, Type B retained
4. Context reduced by 50%

**Voiceover:**
"But what about all these patches? Won't the prompt grow forever?

That's where Semantic Purge comes in. We classify patches into two types:

Type A - syntax fixes, like 'output valid JSON.' These are model defects that newer models fix automatically.

Type B - business knowledge, like 'fiscal year starts in July.' These are world truths that models can't learn.

When you upgrade models, we automatically delete Type A patches. Our experiments show 40 to 60% context reduction while maintaining 100% accuracy."

---

## Demo: Multi-Agent Workflow (1:45 - 2:10)

**[SCREEN: Terminal showing multi-agent orchestration]**

```bash
$ python experiments/multi_agent_rag_experiment.py

Multi-Agent RAG Chain Experiment
================================

Baseline (without SCAK):
  Workflow success rate: 50.0%
  Laziness detected: 12
  Laziness corrected: 0

With SCAK:
  Workflow success rate: 80.0%
  Laziness detected: 12
  Laziness corrected: 8 (67% correction)

✅ +30% improvement in workflow success
```

**Voiceover:**
"It works across complex multi-agent workflows too. In this experiment with a supervised RAG chain, SCAK improved success rate by 30 percent - from 50 to 80 percent - by catching and correcting laziness across multiple agents."

---

## Installation & Getting Started (2:10 - 2:25)

**[SCREEN: Terminal showing installation and quick start]**

```bash
$ pip install scak

$ python
>>> from src.kernel.auditor import CompletenessAuditor
>>> auditor = CompletenessAuditor(teacher_model="o1-preview")
>>> result = await auditor.audit_give_up(
...     user_prompt="Find logs",
...     agent_response="No logs found",
...     context={}
... )
>>> if result.teacher_found_data:
...     # Apply competence patch
...     apply_patch(result.competence_patch)
```

**Voiceover:**
"Getting started is simple. Install with pip, initialize the auditor with your teacher model, and start catching laziness.

The framework is production-ready - type-safe, async-first, with 183 comprehensive tests."

---

## Closing (2:25 - 2:30)

**[SCREEN: GitHub stars/fork buttons, PyPI badge]**

**Text on screen:**
```
🔗 GitHub: github.com/imran-siddique/self-correcting-agent-kernel
📦 PyPI: pip install scak
📚 Docs: Full wiki and examples
⭐ Star us on GitHub!
```

**Voiceover:**
"Check out the full documentation, examples, and research papers on GitHub. It's open source and MIT licensed. We'd love your contributions!"

---

## B-Roll Suggestions

Throughout the video, overlay relevant graphics:
- Architecture diagrams (dual-loop, three-tier memory)
- Result tables from experiments
- Code snippets
- Performance graphs

## Technical Setup

**Recording:**
1. Use OBS Studio for screen recording
2. 1920x1080 resolution
3. Highlight cursor/clicks with tool like ScreenBrush

**Editing:**
1. Add subtitles (for accessibility)
2. Background music (subtle, non-distracting)
3. Transitions between sections
4. Zoom in on important terminal output

**Audio:**
1. Clear voiceover (use good microphone)
2. Remove background noise
3. Normalize audio levels

**Upload:**
1. YouTube (unlisted or public)
2. Embed in README
3. Share on Twitter, LinkedIn

## Alternative: Live Demo Format

If screen recording feels too polished, consider a live walkthrough:
- More authentic
- Show real failures and recoveries
- Explain decisions in real-time
- Can be recorded in one take

## Key Points to Emphasize

1. **Problem is real:** Agents get lazy in production
2. **Solution is practical:** Not just theory - production-ready
3. **Results are validated:** Statistical analysis, multiple experiments
4. **Easy to use:** 3 lines of code to get started
5. **Open source:** MIT license, community-driven

---

**Last Updated:** 2026-01-18  
**Version:** 1.0
