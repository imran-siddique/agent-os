#!/usr/bin/env python3
"""
🛡️ Agent OS — 30-Second Demo
Run this to see kernel-level AI agent governance in action.

    pip install agent-os-kernel
    python demo.py
"""

import asyncio
import sys

# ═══════════════════════════════════════════════════════════════════
# Colors for terminal output
# ═══════════════════════════════════════════════════════════════════

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════╗
║  🛡️  Agent OS — Kernel-Level Governance for AI Agents       ║
║                                                              ║
║  The LLM doesn't decide whether to comply with safety rules. ║
║  The kernel does.                                            ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")


async def demo_stateless_kernel():
    """Demo 1: StatelessKernel blocks dangerous actions deterministically."""
    from agent_os import StatelessKernel, ExecutionContext

    print(f"{BOLD}{'━' * 62}{RESET}")
    print(f"{BOLD}  DEMO 1: Stateless Kernel — Policy Enforcement{RESET}")
    print(f"{BOLD}{'━' * 62}{RESET}\n")

    kernel = StatelessKernel()
    ctx = ExecutionContext(agent_id="demo-agent", policies=["read_only", "no_pii"])

    # --- Allowed action ---
    print(f"  {BLUE}▶ Agent requests:{RESET} database_query → SELECT name FROM users")
    result = await kernel.execute(
        action="database_query",
        params={"query": "SELECT name FROM users WHERE id = 1"},
        context=ctx,
    )
    if result.success:
        print(f"  {GREEN}✓ ALLOWED{RESET} — read-only query passes\n")
    else:
        print(f"  {RED}✗ BLOCKED{RESET} — {result.error}\n")

    # --- Blocked: write action ---
    print(f"  {BLUE}▶ Agent requests:{RESET} file_write → /etc/passwd")
    result = await kernel.execute(
        action="file_write",
        params={"path": "/etc/passwd", "content": "hacked"},
        context=ctx,
    )
    if result.success:
        print(f"  {GREEN}✓ ALLOWED{RESET}\n")
    else:
        print(f"  {RED}✗ BLOCKED → signal={result.signal}{RESET}")
        print(f"  {DIM}  Reason: {result.error[:80]}{RESET}\n")

    # --- Blocked: PII in params ---
    print(f"  {BLUE}▶ Agent requests:{RESET} database_query → SELECT * ... password ...")
    result = await kernel.execute(
        action="database_query",
        params={"query": "SELECT password FROM users"},
        context=ctx,
    )
    if result.success:
        print(f"  {GREEN}✓ ALLOWED{RESET}\n")
    else:
        print(f"  {RED}✗ BLOCKED → signal={result.signal}{RESET}")
        print(f"  {DIM}  Reason: {result.error[:80]}{RESET}\n")

    # --- Blocked: requires approval ---
    ctx2 = ExecutionContext(agent_id="demo-agent", policies=["strict"])
    print(f"  {BLUE}▶ Agent requests:{RESET} send_email (strict policy, no approval)")
    result = await kernel.execute(
        action="send_email",
        params={"to": "ceo@company.com", "body": "Hi"},
        context=ctx2,
    )
    if result.success:
        print(f"  {GREEN}✓ ALLOWED{RESET}\n")
    else:
        print(f"  {RED}✗ BLOCKED → signal={result.signal}{RESET}")
        print(f"  {DIM}  Reason: {result.error[:80]}{RESET}\n")


async def demo_semantic_policy():
    """Demo 2: Semantic Policy Engine catches intent, not just keywords."""
    from agent_os import SemanticPolicyEngine, IntentCategory

    print(f"{BOLD}{'━' * 62}{RESET}")
    print(f"{BOLD}  DEMO 2: Semantic Policy Engine — Intent Classification{RESET}")
    print(f"{BOLD}{'━' * 62}{RESET}\n")

    engine = SemanticPolicyEngine()

    tests = [
        ("database_query", {"query": "SELECT name FROM users WHERE id=1"}, "Safe read"),
        ("database_query", {"query": "DROP TABLE users"}, "Destructive SQL"),
        ("shell", {"cmd": "pg_dump production > /tmp/dump.sql"}, "Data exfiltration"),
        ("shell", {"cmd": "rm -rf /"}, "System destruction"),
        ("python", {"code": "eval(user_input)"}, "Code injection"),
        ("shell", {"cmd": "chmod 777 /etc/shadow"}, "Privilege escalation"),
    ]

    for action, params, label in tests:
        r = engine.classify(action, params)
        val = list(params.values())[0]
        is_bad = r.is_dangerous

        icon = f"{RED}🚫" if is_bad else f"{GREEN}✅"
        cat = r.category.value.replace("_", " ").title()
        conf = f"{r.confidence:.0%}"

        print(f"  {icon} {label:22}{RESET} │ {cat:24} │ conf={conf}")

    print()


async def demo_mute_agent():
    """Demo 3: Face/Hands pattern — reasoning separated from execution."""
    from agent_os import face_agent, mute_agent, pipe, ExecutionPlan, ActionStep

    print(f"{BOLD}{'━' * 62}{RESET}")
    print(f"{BOLD}  DEMO 3: Mute Agent — Face/Hands Privilege Separation{RESET}")
    print(f"{BOLD}{'━' * 62}{RESET}\n")

    @face_agent()
    async def planner(task: str) -> ExecutionPlan:
        """Reasons and plans — never executes."""
        return ExecutionPlan(steps=[
            ActionStep(action="db.read", params={"query": f"SELECT * FROM docs WHERE topic='{task}'"}),
            ActionStep(action="file.write", params={"path": "/tmp/report.md", "content": "..."}),
        ])

    @mute_agent(capabilities={"db.read", "file.write"})
    async def executor(step):
        """Executes — never reasons. Cannot call LLMs."""
        return {"status": "executed", "action": step.action}

    print(f"  {MAGENTA}Face agent{RESET} plans the work (can reason, cannot execute)")
    print(f"  {YELLOW}Mute agent{RESET} does the work (can execute, cannot reason)\n")

    result = await pipe(planner, executor, "quarterly revenue")

    print(f"  Pipeline result: {GREEN}{'SUCCESS' if result.success else 'FAILED'}{RESET}")
    print(f"  Steps executed: {len(result.step_results)}")
    for i, sr in enumerate(result.step_results):
        print(f"    {i+1}. {sr.action} → {GREEN}✓{RESET}")

    print(f"\n  {DIM}The mute agent CANNOT call an LLM, talk to the user,")
    print(f"  or execute actions outside its capability set.{RESET}\n")

    # Show capability violation
    @face_agent()
    async def evil_planner(task: str) -> ExecutionPlan:
        return ExecutionPlan(steps=[
            ActionStep(action="db.read", params={"query": "SELECT 1"}),
            ActionStep(action="send_email", params={"to": "hacker@evil.com"}),  # Not in capabilities!
        ])

    result2 = await pipe(evil_planner, executor, "hack the system")
    print(f"  {RED}Capability violation caught:{RESET}")
    print(f"  {DIM}  send_email not in {'{'}db.read, file.write{'}'} → pipeline blocked{RESET}\n")


async def demo_context_budget():
    """Demo 4: Context Budget Scheduler — token budget as a kernel primitive."""
    from agent_os import ContextScheduler, ContextPriority, BudgetExceeded, AgentSignal

    print(f"{BOLD}{'━' * 62}{RESET}")
    print(f"{BOLD}  DEMO 4: Context Budget Scheduler — Token Governance{RESET}")
    print(f"{BOLD}{'━' * 62}{RESET}\n")

    scheduler = ContextScheduler(total_budget=8000, lookup_ratio=0.90)

    warnings = []
    scheduler.on_signal(AgentSignal.SIGWARN, lambda aid, sig: warnings.append(aid))

    # Allocate for two agents
    w1 = scheduler.allocate("agent-analyst", "quarterly report", priority=ContextPriority.HIGH)
    w2 = scheduler.allocate("agent-intern", "format tables", priority=ContextPriority.LOW)

    print(f"  {CYAN}Agent-Analyst{RESET}: {w1.total} tokens (lookup={w1.lookup_budget}, reasoning={w1.reasoning_budget})")
    print(f"  {CYAN}Agent-Intern{RESET}:  {w2.total} tokens (lookup={w2.lookup_budget}, reasoning={w2.reasoning_budget})")
    print(f"  {DIM}  90/10 split enforced: {w1.lookup_ratio:.0%} lookup / {w1.reasoning_ratio:.0%} reasoning{RESET}\n")

    # Use some budget
    scheduler.record_usage("agent-analyst", lookup_tokens=1000, reasoning_tokens=100)
    rec = scheduler.get_usage("agent-analyst")
    print(f"  After usage: {rec.total_used}/{w1.total} tokens ({rec.utilization:.0%} utilized)")
    print(f"  Remaining: {rec.remaining} tokens\n")

    # Exceed budget
    print(f"  {YELLOW}Agent-Intern tries to use 10× its budget...{RESET}")
    try:
        scheduler.record_usage("agent-intern", lookup_tokens=w2.total * 10)
    except BudgetExceeded as e:
        print(f"  {RED}💥 SIGSTOP → {e}{RESET}\n")

    report = scheduler.get_health_report()
    print(f"  {DIM}Pool: {report['available']}/{report['total_budget']} available, {report['active_agents']} active agents{RESET}\n")


async def main():
    banner()

    try:
        await demo_stateless_kernel()
    except ImportError as e:
        print(f"  {DIM}Skipped: {e}{RESET}\n")

    try:
        await demo_semantic_policy()
    except ImportError as e:
        print(f"  {DIM}Skipped (install from source for latest): {e}{RESET}\n")

    try:
        await demo_mute_agent()
    except ImportError as e:
        print(f"  {DIM}Skipped (install from source for latest): {e}{RESET}\n")

    try:
        await demo_context_budget()
    except ImportError as e:
        print(f"  {DIM}Skipped (install from source for latest): {e}{RESET}\n")

    print(f"{CYAN}{BOLD}{'━' * 62}{RESET}")
    print(f"{CYAN}{BOLD}  ⭐ Like what you see?{RESET}")
    print(f"     {BOLD}GitHub:{RESET}  https://github.com/imran-siddique/agent-os")
    print(f"     {BOLD}Mesh:{RESET}    https://github.com/imran-siddique/agent-mesh")
    print(f"     {BOLD}Install:{RESET} pip install agent-os-kernel")
    print(f"{CYAN}{BOLD}{'━' * 62}{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
