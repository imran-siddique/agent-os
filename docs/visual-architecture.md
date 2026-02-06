# Agent OS Visual Architecture

This document provides visual diagrams of the Agent OS architecture, request flow, and component interactions.

## System Overview

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              AGENT OS RUNTIME                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                        USER SPACE (Ring 3)                               │  ║
║  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                │  ║
║  │  │   LLM Agent   │  │   LLM Agent   │  │   LLM Agent   │                │  ║
║  │  │  (GPT-4/etc)  │  │  (Claude/etc) │  │ (Custom/etc)  │                │  ║
║  │  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘                │  ║
║  │          │                  │                  │                         │  ║
║  │          └──────────────────┼──────────────────┘                         │  ║
║  │                             │                                            │  ║
║  │                    ┌────────▼────────┐                                   │  ║
║  │                    │   SYSCALL API   │                                   │  ║
║  │                    │  SYS_READ/WRITE │                                   │  ║
║  │                    │  SYS_EXEC/SIGNAL│                                   │  ║
║  │                    └────────┬────────┘                                   │  ║
║  └─────────────────────────────┼───────────────────────────────────────────┘  ║
║                                │                                              ║
║  ══════════════════════════════╪══════════════════════════════════════════    ║
║                    KERNEL BOUNDARY (CANNOT BE BYPASSED)                       ║
║  ══════════════════════════════╪══════════════════════════════════════════    ║
║                                │                                              ║
║  ┌─────────────────────────────▼───────────────────────────────────────────┐  ║
║  │                       KERNEL SPACE (Ring 0)                              │  ║
║  │                                                                          │  ║
║  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  ║
║  │  │   POLICY    │  │   FLIGHT    │  │   SIGNAL    │  │    VFS      │     │  ║
║  │  │   ENGINE    │  │  RECORDER   │  │ DISPATCHER  │  │  MANAGER    │     │  ║
║  │  │             │  │             │  │             │  │             │     │  ║
║  │  │ - Rules     │  │ - Audit     │  │ - SIGSTOP   │  │ - /mem/     │     │  ║
║  │  │ - Enforce   │  │ - Merkle    │  │ - SIGKILL   │  │ - /state/   │     │  ║
║  │  │ - Deny      │  │ - Replay    │  │ - SIGPOLICY │  │ - /policy/  │     │  ║
║  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │  ║
║  │                                                                          │  ║
║  └──────────────────────────────────────────────────────────────────────────┘  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## Request Flow: Tool Execution

This diagram shows how an agent's request to execute a tool flows through the kernel.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        TOOL EXECUTION REQUEST FLOW                            │
└──────────────────────────────────────────────────────────────────────────────┘

     Agent (User Space)                    Kernel (Ring 0)
           │                                      │
           │  1. SYS_EXEC("delete_file",         │
           │              "/data/report.pdf")     │
           ├─────────────────────────────────────►│
           │                                      │
           │                          ┌───────────▼───────────┐
           │                          │    POLICY ENGINE      │
           │                          │                       │
           │                          │  Check: "delete_file" │
           │                          │  Path: "/data/*"      │
           │                          │  Agent: did:mesh:abc  │
           │                          │  Trust: 0.72          │
           │                          └───────────┬───────────┘
           │                                      │
           │                          ┌───────────▼───────────┐
           │                          │   POLICY DECISION     │
           │                          │                       │
           │                          │  Rule: "no-delete"    │
           │                          │  Result: DENY ❌       │
           │                          └───────────┬───────────┘
           │                                      │
           │                          ┌───────────▼───────────┐
           │                          │   FLIGHT RECORDER     │
           │                          │                       │
           │                          │  Log: {               │
           │                          │    action: "delete",  │
           │                          │    result: "denied",  │
           │                          │    agent: "did:...",  │
           │                          │    time: "..."        │
           │                          │  }                    │
           │                          └───────────┬───────────┘
           │                                      │
           │                          ┌───────────▼───────────┐
           │                          │  SIGNAL DISPATCHER    │
           │                          │                       │
           │                          │  Send: SIGPOLICY      │
           │                          │  (Policy violation)   │
           │                          └───────────┬───────────┘
           │                                      │
           │  2. SIGPOLICY received              │
           │◄─────────────────────────────────────┤
           │                                      │
           │  3. Agent enters STOPPED state       │
           │     (Cannot execute further)         │
           ▼                                      ▼
```

## Request Flow: Allowed Action

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        ALLOWED ACTION REQUEST FLOW                            │
└──────────────────────────────────────────────────────────────────────────────┘

     Agent (User Space)                    Kernel (Ring 0)
           │                                      │
           │  1. SYS_EXEC("read_file",           │
           │              "/data/report.pdf")     │
           ├─────────────────────────────────────►│
           │                                      │
           │                          ┌───────────▼───────────┐
           │                          │    POLICY ENGINE      │
           │                          │                       │
           │                          │  Check: "read_file"   │
           │                          │  Path: "/data/*"      │
           │                          │  Agent: did:mesh:abc  │
           │                          │  Trust: 0.72          │
           │                          └───────────┬───────────┘
           │                                      │
           │                          ┌───────────▼───────────┐
           │                          │   POLICY DECISION     │
           │                          │                       │
           │                          │  Rule: "allow-read"   │
           │                          │  Result: ALLOW ✅      │
           │                          └───────────┬───────────┘
           │                                      │
           │                          ┌───────────▼───────────┐
           │                          │   TOOL EXECUTOR       │
           │                          │                       │
           │                          │  Sandbox: Docker      │
           │                          │  Action: read_file    │
           │                          │  Timeout: 30s         │
           │                          └───────────┬───────────┘
           │                                      │
           │                          ┌───────────▼───────────┐
           │                          │   FLIGHT RECORDER     │
           │                          │                       │
           │                          │  Log: {               │
           │                          │    action: "read",    │
           │                          │    result: "success", │
           │                          │    duration: "45ms"   │
           │                          │  }                    │
           │                          └───────────┬───────────┘
           │                                      │
           │  2. Result: file_contents           │
           │◄─────────────────────────────────────┤
           │                                      │
           │  3. Agent continues execution        │
           ▼                                      ▼
```

## Virtual File System Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              AGENT VFS STRUCTURE                              │
└──────────────────────────────────────────────────────────────────────────────┘

/agent/[agent-did]/
│
├── mem/                          ← Memory subsystem
│   │
│   ├── working/                  ← Ephemeral scratchpad
│   │   ├── current_task.json        (cleared on restart)
│   │   └── temp_calculations.json
│   │
│   ├── episodic/                 ← Experience logs  
│   │   ├── session_001.json         (mount: ChromaDB)
│   │   ├── session_002.json         (mount: LanceDB)
│   │   └── ...
│   │
│   └── semantic/                 ← Knowledge store
│       ├── domain/                  (mount: Pinecone)
│       └── procedures/              (mount: Weaviate)
│
├── state/                        ← Checkpoints & snapshots
│   │
│   ├── checkpoints/              ← SIGUSR1 triggers
│   │   ├── 2026-02-06T22:00:00.snap
│   │   └── 2026-02-06T21:45:00.snap
│   │
│   └── config.yaml               ← Agent configuration
│
├── policy/                       ← Read-only from user space
│   │
│   ├── rules.yaml                ← Active policy rules
│   ├── capabilities.json         ← Allowed capabilities
│   └── trust.json                ← Current trust score
│
├── ipc/                          ← Inter-process communication
│   │
│   ├── inbox/                    ← Incoming messages (FIFO)
│   ├── outbox/                   ← Outgoing messages
│   └── pipes/                    ← Named pipes for sync
│
└── logs/                         ← Flight recorder output
    ├── audit.log                 ← Tamper-evident (Merkle)
    └── metrics.log               ← Performance data
```

## Signal Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              SIGNAL HANDLING                                  │
└──────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────┐
                    │            SIGNAL DISPATCHER            │
                    │                                         │
                    │  Pending Signals Queue:                 │
                    │  ┌────┬────┬────┬────┬────┐            │
                    │  │ 9  │ 8  │ 4  │ 1  │ 2  │            │
                    │  └────┴────┴────┴────┴────┘            │
                    │   ▲                                     │
                    │   │ Priority: SIGKILL > SIGPOLICY >    │
                    │   │           SIGTRUST > others         │
                    └───┼─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        ▼               ▼               ▼               ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ SIGSTOP │    │ SIGKILL │    │SIGPOLICY│    │SIGTRUST │
   │  (1)    │    │  (4)    │    │  (8)    │    │  (9)    │
   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ Pause   │    │Terminate│    │ Violate │    │ Trust   │
   │ Agent   │    │   NOW   │    │ Policy  │    │ Breach  │
   │ Inspect │    │ No Mask │    │→SIGKILL │    │→SIGKILL │
   └─────────┘    └─────────┘    └─────────┘    └─────────┘
        │                              │              │
        │                              │              │
        ▼                              ▼              ▼
   ┌─────────┐                   ┌─────────────────────────┐
   │ SIGCONT │                   │   KERNEL PANIC          │
   │ Resume  │                   │   - Log final state     │
   └─────────┘                   │   - Notify sponsor      │
                                 │   - Revoke credentials  │
                                 └─────────────────────────┘
```

## Policy Engine Decision Tree

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          POLICY ENGINE DECISION TREE                          │
└──────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │ Incoming Action │
                              │                 │
                              │ agent: did:...  │
                              │ action: write   │
                              │ resource: /db/* │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Check Deny List │
                              │                 │
                              │ Is action in    │
                              │ explicit deny?  │
                              └────────┬────────┘
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                         YES                        NO
                          │                         │
                          ▼                         ▼
                   ┌─────────────┐         ┌─────────────────┐
                   │    DENY     │         │ Check Allow List│
                   │ + SIGPOLICY │         │                 │
                   └─────────────┘         │ Is action in    │
                                           │ explicit allow? │
                                           └────────┬────────┘
                                                    │
                                       ┌────────────┴────────────┐
                                       │                         │
                                      YES                        NO
                                       │                         │
                                       ▼                         ▼
                               ┌─────────────┐         ┌─────────────────┐
                               │ Check Trust │         │ Check Capability│
                               │   Score     │         │                 │
                               │             │         │ Has required    │
                               │ score >=    │         │ capability?     │
                               │ threshold?  │         └────────┬────────┘
                               └──────┬──────┘                  │
                                      │                ┌────────┴────────┐
                          ┌───────────┴───────────┐    │                 │
                          │                       │   YES                NO
                         YES                      NO   │                 │
                          │                       │    ▼                 ▼
                          ▼                       ▼  ┌─────┐      ┌─────────────┐
                    ┌───────────┐          ┌─────────────┐│     │    DENY     │
                    │   ALLOW   │          │    DENY     ││     │ No capability│
                    │ Execute   │          │ Low trust   ││     └─────────────┘
                    │ action    │          └─────────────┘│
                    └───────────┘                         │
                                                          ▼
                                                   ┌─────────────┐
                                                   │ Default Rule│
                                                   │             │
                                                   │ DENY if not │
                                                   │ explicit    │
                                                   └─────────────┘
```

## Layer Interaction Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LAYER INTERACTIONS                                  │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            LAYER 4: INTELLIGENCE                             │
│                                                                              │
│    ┌──────────────────────┐          ┌──────────────────────┐               │
│    │        SCAK          │◄────────►│     Mute Agent       │               │
│    │  Self-Correction     │          │  Reasoning/Exec      │               │
│    └──────────┬───────────┘          └──────────┬───────────┘               │
│               │                                  │                           │
│               │  Laziness detection              │  Constraint pruning       │
│               │  Differential audit              │  Semantic handshake       │
│               │                                  │                           │
└───────────────┼──────────────────────────────────┼───────────────────────────┘
                │                                  │
                ▼                                  ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 3: FRAMEWORK                                  │
│                                                                               │
│    ┌────────────────────────────────────────────────────────────────────┐    │
│    │                      AGENT CONTROL PLANE                            │    │
│    │                                                                     │    │
│    │    ┌─────────────────────────────────────────────────────────┐     │    │
│    │    │                    KERNEL (Ring 0)                       │     │    │
│    │    │  Policy Engine ◄─► Flight Recorder ◄─► Signal Dispatch  │     │    │
│    │    └─────────────────────────┬───────────────────────────────┘     │    │
│    │                              │                                      │    │
│    │    ══════════════════════════╪═══════════════════════════════      │    │
│    │                              │                                      │    │
│    │    ┌─────────────────────────▼───────────────────────────────┐     │    │
│    │    │                   USER SPACE (Ring 3)                    │     │    │
│    │    │              Agent Logic  ◄─►  LLM Generation           │     │    │
│    │    └─────────────────────────────────────────────────────────┘     │    │
│    └────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                │                    │                    │
                ▼                    ▼                    ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                        LAYER 2: INFRASTRUCTURE                                │
│                                                                               │
│    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│    │       IATP       │  │       AMB        │  │       ATR        │          │
│    │                  │  │                  │  │                  │          │
│    │  Trust Protocol  │  │  Message Bus     │  │  Tool Registry   │          │
│    │  - Sidecar proxy │  │  - Pub/Sub       │  │  - Discovery     │          │
│    │  - IPC pipes     │  │  - Priority      │  │  - Sandbox       │          │
│    │  - Handshake     │  │  - Backpressure  │  │  - Execution     │          │
│    └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘          │
│             │                     │                     │                     │
└─────────────┼─────────────────────┼─────────────────────┼─────────────────────┘
              │                     │                     │
              ▼                     ▼                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 1: PRIMITIVES                                  │
│                                                                               │
│    ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│    │ Primitives │  │    CMVK    │  │    CaaS    │  │    EMK     │            │
│    │            │  │            │  │            │  │            │            │
│    │ - Failures │  │ - Drift    │  │ - RAG      │  │ - Episodic │            │
│    │ - Models   │  │ - Verify   │  │ - Context  │  │ - Memory   │            │
│    │ - Types    │  │ - Halluc.  │  │ - Pipeline │  │ - Ledger   │            │
│    └────────────┘  └────────────┘  └────────────┘  └────────────┘            │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        KUBERNETES DEPLOYMENT                                  │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              NAMESPACE: agent-os                             │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                           POD: agent-worker-1                          │ │
│  │                                                                        │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │ │
│  │  │   CONTAINER    │  │   CONTAINER    │  │   CONTAINER    │           │ │
│  │  │   agent-os     │  │   iatp-sidecar │  │   llm-agent    │           │ │
│  │  │   (kernel)     │  │   (trust)      │  │   (user space) │           │ │
│  │  │                │  │                │  │                │           │ │
│  │  │  - Policy      │◄─┤  - Trust verify│◄─┤  - GPT-4       │           │ │
│  │  │  - Recorder    │  │  - IPC proxy   │  │  - Agent logic │           │ │
│  │  │  - Signals     │  │  - Handshakes  │  │  - Tool calls  │           │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘           │ │
│  │          │                   │                   │                     │ │
│  │          └───────────────────┴───────────────────┘                     │ │
│  │                              │                                         │ │
│  │                    ┌─────────▼─────────┐                              │ │
│  │                    │    SHARED VOLUME  │                              │ │
│  │                    │    /agent/vfs/    │                              │ │
│  │                    └───────────────────┘                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │    SERVICE      │  │    SERVICE      │  │   CONFIGMAP     │              │
│  │  agent-os-api   │  │   iatp-mesh     │  │  policies.yaml  │              │
│  │  :8080          │  │   :9090         │  │                 │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## See Also

- [Architecture Overview](architecture.md)
- [Kernel Internals](kernel-internals.md)
- [Security Specification](security-spec.md)
- [Signal Handling](signal-handling.md)
