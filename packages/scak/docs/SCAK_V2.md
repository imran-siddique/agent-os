# **SCAK v2 - The Evolutionary Swarm Kernel**

## **🚀 What's New in v2?**

SCAK v2 extends the foundation from **"Fixing Errors"** (v1) to **"Optimizing Swarms"** (v2). It addresses the **Complexity Wall** in multi-agent systems with three new capabilities:

1. **Adaptive Reward Shaping** - Agents evolve behavior from feedback without retraining
2. **Emergence Monitoring** - Detect anomalies that only exist in agent interactions
3. **Evolvable Orchestration** - Hot-swap underperforming agents mid-flight

---

## **1. Adaptive Reward Shaping (`src/kernel/evolution.py`)**

### **Problem**
Hard-coded prompts fail in dynamic swarms. User preferences change ("be more concise"), but retraining is expensive.

### **Solution: RLAIF-lite**
Dynamically adjust agent behavior via **context injection + rubric weighting**.

```python
from src.kernel.evolution import RewardShaper
from src.kernel.schemas import SwarmTrace

# Initialize shaper with baseline rubric
shaper = RewardShaper()

# Agent receives feedback
trace = SwarmTrace(
    original_intent="Analyze customer data",
    agent_ids=["analyst-001"]
)

# Shape reward from user feedback
update = await shaper.shape_reward(trace, "Too verbose")

print(f"New weights: {update.rubric_after.weights}")
# Output: {'conciseness': 0.45, 'accuracy': 0.45, 'thoroughness': 0.1}

print(f"Behavioral nudge: {update.prompt_nudge}")
# Output: "Prioritize conciseness +15%. Reduce thoroughness -10%."
```

### **Key Features**
- **Online Learning**: No fine-tuning required
- **Rollback Support**: Revert to previous rubric versions
- **Integration with v1**: Auditor's laziness detection → negative reward signal

### **Architecture**
```
Feedback → FeedbackAnalyzer → Correction Vector
    ↓
RubricOptimizer → New Weights → NudgeGenerator
    ↓                              ↓
History         →    Prompt Injection
```

---

## **2. Emergence Monitoring (`src/kernel/governance_v2.py`)**

### **Problem**
Individual messages look safe, but agent *interactions* create emergent failures:
- **Infinite loops**: Agent A and B in circular approval
- **Goal drift**: Swarm drifts from original intent
- **Echo chambers**: Agents repeating same content

### **Solution: Graph + Semantic Analysis**
Monitor the **topology** of agent interactions, not just individual messages.

```python
from src.kernel.governance_v2 import EmergenceMonitor
from src.kernel.schemas import SwarmTrace, SwarmStep

# Initialize monitor
monitor = EmergenceMonitor(drift_threshold=0.4, echo_threshold=0.9)

# Initialize with original intent
trace = SwarmTrace(
    original_intent="Approve budget request",
    agent_ids=["manager-a", "manager-b"]
)
monitor.initialize_trace(trace)

# Check each interaction step
step = SwarmStep(
    source="manager-a",
    target="manager-b",
    content="Please approve first"
)

decision = await monitor.check_step(step)

if decision.is_anomaly:
    print(f"⚠️ Anomaly: {decision.type}")
    print(f"Action: {decision.suggested_action}")
    # Output: "⚠️ Anomaly: INFINITE_LOOP"
    #         "Action: CIRCUIT_BREAK"
```

### **Detection Vectors**
1. **Cycles** (Infinite Loops)
   - Uses networkx for graph topology analysis
   - Detects circular dependencies: A → B → A

2. **Semantic Drift**
   - Compares current discussion with original intent
   - Uses cosine distance on embeddings
   - Triggers when distance > threshold

3. **Echo Chambers**
   - Detects repetitive content (similarity > 0.9)
   - Checks last 3-5 messages

4. **Escalation Spirals**
   - Detects "After you" / "Let me check with..." patterns
   - Flags when agents keep deferring (≥3 in last 5 messages)

### **Integration with v1**
```python
from src.kernel.governance_v2 import triage_anomaly

# Bridge to v1 FailureTriage
decision = await monitor.check_step(step)
action = triage_anomaly(decision)

if action == "CIRCUIT_BREAK":
    # Terminate swarm immediately
    orchestrator.terminate_swarm()
```

---

## **3. Evolvable Orchestration (`src/agents/swarm.py`)**

### **Problem**
Fixed agent roles fail when performance varies. A "basic analyst" might struggle, but you can't swap to "senior analyst" without interruption.

### **Solution: Hot-Swapping**
Dynamically replace underperforming agents based on reward scores.

```python
from src.agents.swarm import EvolvableOrchestrator, AgentPool
from src.agents.orchestrator import AgentSpec, AgentRole

# Create agent pool with tiers
pool = AgentPool()

agents = [
    AgentSpec(
        agent_id="analyst-basic",
        role=AgentRole.ANALYST,
        model="gpt-4o-mini"
    ),
    AgentSpec(
        agent_id="analyst-senior",
        role=AgentRole.ANALYST,
        model="o1-preview"
    )
]

pool.register_agent(agents[0], tier=1)
pool.register_agent(agents[1], tier=3)

# Create orchestrator
orchestrator = EvolvableOrchestrator(
    agents=[agents[0]],  # Start with basic
    agent_pool=pool,
    performance_threshold=0.70,
    swap_enabled=True
)

# Orchestrator monitors performance
# If reward < 0.70, automatically swaps to tier 3 agent
```

### **Hot-Swap Lifecycle**
1. **Monitor**: Track reward_score, success_rate, latency
2. **Detect**: Performance < threshold (default 0.70)
3. **Find**: Locate higher-tier agent with same role
4. **Swap**: Replace agent + transfer context
5. **Resume**: Continue execution seamlessly

### **Features**
- **Tier System**: Basic (1) → Standard (2) → Senior (3)
- **Context Handover**: Transfer conversation history
- **Swap History**: Full audit trail
- **Force Swap**: Manual intervention support

---

## **4. Integration with v1 Architecture**

SCAK v2 builds directly on v1 primitives:

| v1 Component | v2 Integration | Effect |
|--------------|----------------|--------|
| **CompletenessAuditor** | Feeds negative reward to RewardShaper | Swarm learns to be less lazy |
| **MemoryController** | Stores evolution snapshots | Rollback capability |
| **FailureTriage** | Routes anomalies to EmergenceMonitor | Circuit breaking |

---

## **5. Quick Start - v2**

### **Installation**
```bash
# Install v2 dependencies
pip install networkx>=3.0 numpy>=1.24.0

# Or install from requirements
pip install -r requirements.txt
```

### **Run the Demo**
```bash
python examples/scak_v2_demo.py
```

**Output:**
```
============================================================
SCAK v2 - Evolutionary Swarm Kernel Demo
============================================================

DEMO 1: Adaptive Reward Shaping
  ✅ Agent behavior evolved from feedback (no retraining)

DEMO 2: Emergence Monitoring
  ✅ Detected infinite loop and triggered circuit breaker

DEMO 3: Evolvable Orchestrator
  ✅ Hot-swapped analyst-basic → analyst-senior (expected +15% reward)
============================================================
```

---

## **6. API Reference - v2**

### **RewardShaper**
```python
class RewardShaper:
    async def shape_reward(
        self,
        trace: SwarmTrace,
        feedback: str
    ) -> RubricUpdate:
        """Shape reward based on feedback."""
        
    def rollback(self, version: int) -> bool:
        """Rollback to previous rubric version."""
        
    def get_evolution_history(self) -> List[RubricUpdate]:
        """Get reward evolution history."""
```

### **EmergenceMonitor**
```python
class EmergenceMonitor:
    def initialize_trace(self, trace: SwarmTrace):
        """Initialize monitoring for new swarm."""
        
    async def check_step(self, step: SwarmStep) -> AnomalyDecision:
        """Check single step for anomalies."""
        
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
```

### **EvolvableOrchestrator**
```python
class EvolvableOrchestrator(Orchestrator):
    async def submit_task_with_monitoring(
        self,
        description: str,
        rubric: Optional[Rubric] = None
    ) -> str:
        """Submit task with performance monitoring."""
        
    async def force_swap(
        self,
        old_agent_id: str,
        new_agent_id: str
    ) -> bool:
        """Force agent swap."""
        
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get swarm evolution statistics."""
```

---

## **7. Testing**

Run v2 test suite:
```bash
pytest tests/test_scak_v2.py -v
```

**Coverage:**
- ✅ 29 tests (RewardShaper, EmergenceMonitor, EvolvableOrchestrator)
- ✅ Integration tests with v1
- ✅ Edge cases (cycles, drift, swaps)

---

## **8. Roadmap**

### **Phase 1: The Observer (Current - Q1 2026)** ✅
- [x] EmergenceMonitor implementation
- [x] Basic anomaly detection (loops, drift, echo chambers)
- [x] Manual intervention support

### **Phase 2: The Shaper (Q2 2026)**
- [ ] RewardShaper production hardening
- [ ] Real LLM integration for feedback parsing
- [ ] Metrics dashboard

### **Phase 3: The Evolutionary (Q3 2026)**
- [ ] Fully autonomous hot-swapping
- [ ] Multi-swarm coordination
- [ ] Benchmark: 20% performance improvement over 10 iterations

---

## **9. Success Metrics - v2**

| Metric | Target | Status |
|--------|--------|--------|
| **Adaptability** | +20% improvement over 10 iterations | 🔄 In Progress |
| **Safety** | 100% loop detection | ✅ Complete |
| **Efficiency** | 30% token savings via drift detection | 🔄 In Progress |
| **Swap Speed** | <5s context handover | ✅ Complete |

---

## **10. Research Foundation**

SCAK v2 is inspired by:
- **Voyager** (arXiv:2305.16291) - Self-growing skill libraries
- **DEPS** (ICML 2023) - Evolvable production systems
- **AutoGen** (MSR 2023) - Multi-agent coordination
- **RLAIF** (arXiv:2309.00267) - AI feedback for alignment

---

## **11. Contributing to v2**

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Priority areas:**
- Real embedding models (OpenAI, Sentence-Transformers)
- Production message brokers (Redis, Kafka)
- Benchmarks and evaluations
- Documentation improvements

---

## **12. Citation**

If you use SCAK v2 in your research:
```bibtex
@software{scak_v2_2026,
  title = {SCAK v2: The Evolutionary Swarm Kernel},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/imran-siddique/self-correcting-agent-kernel}
}
```

---

**🎯 From Maintenance to Evolution: SCAK v2 enables self-improving, self-correcting swarms.**
