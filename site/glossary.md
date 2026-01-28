---
layout: default
title: Glossary
nav_order: 7
permalink: /glossary/
description: "AI agent terminology glossary - understand the key concepts in autonomous AI systems and Agent OS."
---

# AI Agent Glossary
{: .no_toc }

Key terms and concepts in AI agent development and Agent OS.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## A

### Agent
A software system that perceives its environment and takes actions to achieve goals, typically powered by large language models (LLMs). In Agent OS, agents run in **user space** and are governed by the **kernel**.

### Agent Memory
The data storage systems that allow agents to remember past interactions, learn from experience, and maintain context. See also: **Episodic Memory**, **Semantic Memory**, **Working Memory**.

### AMB (Agent Message Bus)
Agent OS component that provides decoupled communication between agents. Supports multiple backends: Redis, Kafka, NATS, AWS SQS, Azure Service Bus.

### Audit Trail
A chronological record of all agent actions and decisions. In Agent OS, the audit trail is **immutable** (append-only) for compliance and debugging.

---

## C

### CMVK (Cross-Model Verification Kernel)
Agent OS component that detects hallucinations by comparing outputs across multiple LLMs. If models disagree significantly, the output is flagged for review.

### Consensus
In CMVK, the degree of agreement between multiple models on a given output. Typically measured as a percentage (e.g., 90% consensus means 90% of models agree).

### Context Window
The maximum amount of text (measured in tokens) that an LLM can process in a single request. Agent OS helps manage context through the VFS and EMK.

---

## D

### Deterministic Enforcement
The guarantee that policy violations will always be blocked, regardless of agent behavior. Unlike prompt-based safety, the agent cannot choose to ignore rules.

### Drift
In CMVK, the semantic difference between two outputs. High drift indicates significant disagreement or potential hallucination.

---

## E

### EMK (Episodic Memory Kernel)
Agent OS component that provides an immutable, append-only ledger of agent experiences. Enables time-travel debugging and learning from past interactions.

### Episode
A single unit of agent experience in EMK, containing: goal, action, result, and reflection.

---

## F

### Flight Recorder
Agent OS component that captures agent execution traces for debugging. Enables replay of agent decisions at any checkpoint.

---

## G

### Governance
The set of rules, policies, and enforcement mechanisms that control what agents can do. Agent OS provides kernel-level governance.

### Guardrails
Safety mechanisms for AI systems. Traditional guardrails are prompt-based; Agent OS provides kernel-enforced guardrails.

---

## H

### Hallucination
When an LLM generates content that is factually incorrect, nonsensical, or inconsistent with its training data. CMVK helps detect hallucinations through multi-model verification.

---

## I

### IATP (Inter-Agent Trust Protocol)
Agent OS component that provides cryptographic signing and verification of messages between agents. Ensures message authenticity and prevents tampering.

### Immutable
Data that cannot be modified after creation. Agent OS audit trails and episodic memories are immutable for integrity.

---

## K

### Kernel
The core of Agent OS that enforces policies and controls agent execution. Inspired by operating system kernels like Linux.

### Kernel Space
The protected environment where Agent OS runs. Agents cannot directly access kernel space; they must go through defined interfaces.

### KernelSpace (class)
The main Agent OS class that provides policy enforcement, signal handling, and agent governance.

---

## L

### LLM (Large Language Model)
AI models trained on large amounts of text data, capable of understanding and generating human-like text. Examples: GPT-4, Claude, Gemini.

---

## M

### MCP (Model Context Protocol)
A protocol for connecting LLMs to external tools and data sources. Agent OS provides an MCP server for Claude Desktop integration.

### Multi-Agent System
A system with multiple agents that interact, coordinate, and potentially compete. Agent OS provides IATP for trust and AMB for communication.

---

## P

### Policy
A set of rules defining what agents can and cannot do. Policies include blocked actions, blocked patterns, and signal configurations.

### Policy Engine
Agent OS component that evaluates agent actions against active policies and determines whether to allow or block them.

### POSIX
A family of standards for Unix-like operating systems. Agent OS borrows concepts from POSIX including signals and process control.

---

## R

### RAG (Retrieval-Augmented Generation)
A technique that combines LLM generation with information retrieval from external sources. Agent OS CAAS component supports RAG routing.

### Revocation
The process of removing trust from an agent in IATP. Revoked agents cannot communicate with trusted agents.

---

## S

### SCAK (Self-Correcting Agent Kernel)
Agent OS component that enables agents to learn from mistakes through verification-driven correction loops.

### Semantic Memory
Long-term knowledge storage for agents. In Agent OS VFS, accessed at `/mem/semantic/`.

### Signal
A notification sent to an agent to control its execution. Agent OS signals include:
- **SIGKILL**: Terminate immediately (non-catchable)
- **SIGSTOP**: Pause for review (non-catchable)
- **SIGCONT**: Resume execution
- **SIGTERM**: Graceful termination

### Strict Policy
The default Agent OS policy that blocks dangerous operations: file writes/deletes, destructive SQL, shell execution, secret exposure.

---

## T

### Time-Travel Debugging
The ability to replay agent execution from any checkpoint to understand past decisions. Enabled by the Flight Recorder.

### Trust Level
In IATP, the degree of trust assigned to an agent. Levels: HIGH, MEDIUM, LOW, NONE.

### Trust Registry
IATP component that tracks agent identities, public keys, and trust levels.

---

## U

### User Space
The environment where agent code runs. Agents in user space are subject to kernel policies and cannot bypass enforcement.

---

## V

### VFS (Virtual File System)
Agent OS component that provides structured, isolated memory for agents. Paths include:
- `/mem/working/` - Agent scratch space
- `/mem/episodic/` - Historical episodes (read-only)
- `/mem/semantic/` - Long-term knowledge (read-only)
- `/policy/` - Active policies (read-only)
- `/proc/` - Agent process info (read-only)

### Violation
When an agent action matches a blocked rule in a policy. Violations trigger signals (typically SIGKILL).

---

## W

### Working Memory
Short-term, modifiable memory for agents. In Agent OS VFS, accessed at `/mem/working/`.

---

## Related Resources

- [Core Concepts](/docs/concepts/) — Detailed explanations
- [FAQ](/faq/) — Common questions
- [API Reference](/docs/api/) — Technical details
