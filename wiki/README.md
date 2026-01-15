# Self-Correcting Agent Kernel - Documentation Wiki

Welcome to the Self-Correcting Agent Kernel documentation wiki. This directory contains comprehensive guides and references for understanding and using the system.

## 📚 Documentation Index

### Core Architecture

- **[Dual-Loop Architecture](./Dual-Loop-Architecture.md)** - Complete architecture overview
  - Loop 1: Runtime Safety (Constraint Engine)
  - Loop 2: Offline Alignment (Quality & Efficiency)
  - Completeness Auditor and Semantic Purge explained

### Feature Guides

- **[Enhanced Features](./Enhanced-Features.md)** - Advanced features and enhancements
  - Tool Execution Telemetry (False Positive Prevention)
  - Semantic Analysis (Beyond Regex)
  - Nudge Mechanism (Automatic Retry Logic)
  - Value Delivery Metrics (Competence Focus)

- **[Three Failure Types](./Three-Failure-Types.md)** - Implementation guide for specific failures
  - Tool Misuse (Schema Injection)
  - Hallucination (RAG Patch)
  - Policy Violation (Constitutional Update)

### Reference Materials

- **[Reference Implementations](./Reference-Implementations.md)** - Educational implementations
  - Completeness Auditor (simplified)
  - Shadow Teacher (core diagnosis)
  - Memory Manager (lifecycle basics)

- **[Implementation Summary](./Implementation-Summary.md)** - Enhanced features implementation summary
  - Complete overview of enhancements
  - Testing and validation
  - Production readiness

## 🚀 Quick Links

### Getting Started
- [Main README](../README.md) - Project overview and quick start
- [Installation Guide](../README.md#installation) - Setup instructions
- [Examples](../examples/) - Working code examples

### Experiments
- [GAIA Benchmark](../experiments/gaia_benchmark/README.md) - Laziness stress test
- [Chaos Engineering](../experiments/chaos_engineering/README.md) - Robustness test

## 📖 Reading Order

For new users, we recommend reading the documentation in this order:

1. **Start with**: [Main README](../README.md) - Get an overview
2. **Then read**: [Dual-Loop Architecture](./Dual-Loop-Architecture.md) - Understand the core design
3. **Deep dive**: [Enhanced Features](./Enhanced-Features.md) - Learn about advanced capabilities
4. **Explore**: [Reference Implementations](./Reference-Implementations.md) - See simplified examples
5. **Specialize**: [Three Failure Types](./Three-Failure-Types.md) - Understand specific failure handling

## 🎯 Documentation by Use Case

### I want to understand...

**...how the system works:**
- [Dual-Loop Architecture](./Dual-Loop-Architecture.md)

**...what problems it solves:**
- [Dual-Loop Architecture](./Dual-Loop-Architecture.md) - Silent failures and context bloat
- [Enhanced Features](./Enhanced-Features.md) - False positives and competence tracking

**...how to use it:**
- [Main README](../README.md) - API reference and examples
- [Examples Directory](../examples/) - Working code samples

**...how it's implemented:**
- [Reference Implementations](./Reference-Implementations.md) - Simplified code
- [Implementation Summary](./Implementation-Summary.md) - Technical details

**...how to handle specific failures:**
- [Three Failure Types](./Three-Failure-Types.md) - Tool misuse, hallucination, policy violations

## 🔬 Research & Experiments

The system is validated through real-world experiments:

- **Experiment A (GAIA)**: Proves the agent tries harder than standard GPT-4o
- **Experiment B (Amnesia)**: Proves "Scale by Subtraction" prevents context bloat  
- **Experiment C (Chaos)**: Proves self-healing capability without manual intervention

See the [experiments directory](../experiments/) for details.

## 🤝 Contributing

When adding new documentation:
1. Place it in the appropriate section above
2. Update this index
3. Add cross-references to related documents
4. Follow the existing markdown style

## 📝 Documentation Standards

- Use clear, descriptive headings
- Include code examples where applicable
- Add cross-references to related documentation
- Keep technical accuracy high
- Update timestamps when making significant changes

---

**Last Updated**: 2026-01-15

**Maintained by**: Self-Correcting Agent Kernel Team
