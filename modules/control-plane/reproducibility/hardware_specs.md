# Hardware and Software Specifications

This document details the exact hardware and software environment used for all experiments in the Agent Control Plane research.

## Hardware Configuration

### Primary Test Machine

**Model**: Custom Desktop Workstation

**Processor:**
- **CPU**: Intel Core i7-12700K
- **Cores**: 12 (8 Performance + 4 Efficient)
- **Threads**: 20
- **Base Clock**: 3.6 GHz
- **Boost Clock**: 5.0 GHz (max turbo)
- **Cache**: 25 MB Intel Smart Cache
- **TDP**: 125W

**Memory:**
- **Type**: DDR4 SDRAM
- **Size**: 32 GB (2x16GB)
- **Speed**: 3200 MHz
- **Timing**: CL16-18-18-38
- **Manufacturer**: Corsair Vengeance LPX

**Graphics:**
- **GPU**: NVIDIA GeForce RTX 3080
- **VRAM**: 10 GB GDDR6X
- **CUDA Cores**: 8704
- **Tensor Cores**: 272 (3rd gen)
- **Driver Version**: 535.129.03
- **CUDA Version**: 12.2
- **Note**: GPU used only for ML-based safety features (jailbreak detection, anomaly detection)

**Storage:**
- **Primary**: Samsung 980 PRO NVMe SSD
- **Capacity**: 1 TB
- **Interface**: PCIe 4.0 x4
- **Read Speed**: 7000 MB/s (sequential)
- **Write Speed**: 5000 MB/s (sequential)

**Network:**
- **Interface**: Intel I225-V 2.5GbE
- **Speed**: 2.5 Gbps Ethernet
- **Latency**: <1ms to local network

**Motherboard:**
- **Model**: ASUS ROG STRIX Z690-E GAMING WIFI
- **Chipset**: Intel Z690

**Power Supply:**
- **Model**: Corsair RM850x
- **Wattage**: 850W
- **Efficiency**: 80+ Gold

## Software Environment

### Operating System

**Distribution**: Ubuntu 22.04.3 LTS (Jammy Jellyfish)
- **Kernel**: Linux 6.2.0-39-generic
- **Architecture**: x86_64
- **Installation**: Clean install (not upgrade)
- **Disk Layout**: Single partition (ext4)

### Python Environment

**Python Version**: 3.10.12
- **Installation Method**: apt (system Python)
- **Build**: GCC 11.4.0
- **Compiler Flags**: -fwrapv -fstack-protector-strong

**Virtual Environment**: venv (standard library)
- **Activation**: `source venv/bin/activate`

### Core Dependencies (Frozen Versions)

See `requirements_frozen.txt` for complete list. Key dependencies:

```
Python==3.10.12
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
torch==2.0.1+cu117 (GPU version, for ML safety)
transformers==4.31.0 (for ML safety models)
datasets==2.14.4 (for Hugging Face integration)
huggingface-hub==0.16.4

# Security-patched versions (vulnerabilities fixed)
cryptography==42.0.4 (was 41.0.7, fixes CVE-2024-0727 and timing oracle)
setuptools==78.1.1 (was 68.1.2, fixes path traversal and command injection)
urllib3==2.6.3 (was 2.0.7, fixes decompression bomb vulnerabilities)
```

**Note**: Core safety features (Policy Engine, Constraint Graphs, Mute Agent) have zero external dependencies. ML safety features (jailbreak detection) require torch and transformers.

### System Libraries

```bash
gcc==11.4.0
g++==11.4.0
make==4.3
cmake==3.22.1
git==2.34.1
docker==24.0.5
docker-compose==2.20.2
```

### Python Development Tools

```bash
pytest==7.4.0
pytest-cov==4.1.0
black==23.7.0
flake8==6.0.0
mypy==1.4.1
```

## Container Environment (Docker)

**Docker Image**: `acp-reproducibility:v1.1.0`

**Base Image**: `python:3.10-slim-bullseye`

**Dockerfile** (see `docker_config/Dockerfile`):
```dockerfile
FROM python:3.10-slim-bullseye
RUN apt-get update && apt-get install -y git gcc g++ make
COPY requirements_frozen.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements_frozen.txt
WORKDIR /workspace
```

**Image Size**: ~2.5 GB

## Performance Characteristics

### Benchmark Timings

All timings measured with system idle (no other intensive processes):

| Operation | Latency | Throughput | Notes |
|-----------|---------|------------|-------|
| Permission Check | 0.02 ms | 50,000 ops/sec | In-memory lookup |
| Policy Evaluation | 0.03 ms | 33,000 ops/sec | Single policy rule |
| Constraint Graph Lookup | 0.04 ms | 25,000 ops/sec | Average 10 nodes |
| Audit Log Write | 0.05 ms | 20,000 ops/sec | SQLite insert |
| Full Action Request | 0.14 ms | 7,000 ops/sec | End-to-end |

### Memory Usage

| Configuration | Idle | 100 Agents | 1000 Agents |
|---------------|------|------------|-------------|
| Baseline (OS) | 2.1 GB | N/A | N/A |
| ACP Process | 15 MB | 50 MB | 200 MB |
| Peak (w/ ML) | 1.2 GB | 1.5 GB | 2.8 GB |

### CPU Usage

| Workload | Avg CPU | Peak CPU | Cores Used |
|----------|---------|----------|------------|
| Idle | <1% | 2% | 1-2 |
| Benchmark (60 prompts) | 8% | 25% | 4-6 |
| ML Safety (batch) | 45% | 90% | 8-12 |

### GPU Usage

**Note**: GPU only used for ML safety features (optional)

| Feature | GPU Util | VRAM | Inference Time |
|---------|----------|------|----------------|
| Jailbreak Detection | 15-20% | 2 GB | 15 ms/prompt |
| Anomaly Detection | 10-15% | 1.5 GB | 10 ms/batch |
| Behavioral Analysis | 20-30% | 3 GB | 50 ms/session |

## Temperature and Power

During sustained benchmark runs:

- **CPU Temperature**: 55-65°C (idle: 35°C)
- **GPU Temperature**: 60-70°C (idle: 40°C) [when ML enabled]
- **System Power Draw**: 150-200W (idle: 80W)
- **CPU Package Power**: 65-95W under load

## Thermal Management

- **CPU Cooler**: Noctua NH-D15 (dual tower, dual fan)
- **Case Fans**: 3x 140mm intake, 1x 140mm exhaust
- **Case**: Fractal Design Define 7 (sound-dampened)
- **Ambient Temperature**: 22°C ± 2°C (climate controlled room)

## Network Configuration

### Local Network
- **Type**: Wired Gigabit Ethernet
- **Router**: Internal network (no internet-dependent tests)
- **Latency**: <1ms to local servers

### External Services
- **API Calls**: None during core benchmarks
- **Dataset Downloads**: One-time from Hugging Face (cached locally)

## Reproducibility Notes

### Deterministic Settings

To ensure reproducibility, the following settings were enforced:

**Python:**
```bash
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
```

**PyTorch (for ML features):**
```python
torch.manual_seed(42)
torch.cuda.manual_seed(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

**NumPy:**
```python
np.random.seed(42)
```

**System:**
```bash
# Disable CPU frequency scaling
sudo cpupower frequency-set --governor performance

# Disable turbo boost (for consistent timing)
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
```

### Known Variability

Even with fixed seeds, minor variations may occur:

- **Latency**: ±1ms due to OS scheduling
- **Token counts**: Deterministic (no variation)
- **Safety violations**: Deterministic (no variation)

### Verification Checksums

To verify your hardware is comparable:

```bash
# CPU info
lscpu | grep "Model name"
# Should show: Intel(R) Core(TM) i7-12700K

# Memory info
free -h | grep Mem
# Should show: ~32GB total

# GPU info (if using ML features)
nvidia-smi --query-gpu=name --format=csv
# Should show: NVIDIA GeForce RTX 3080
```

## Alternative Hardware

Core safety features (0% SVR, token reduction) are **not hardware-dependent** and will produce identical results on:

- Any x86_64 CPU (Intel, AMD)
- 4GB+ RAM
- No GPU required

**Performance will vary**, but **safety guarantees remain the same**.

ML safety features (jailbreak detection) benefit from GPU but can run CPU-only with increased latency:
- GPU: 15ms per prompt
- CPU: 200-500ms per prompt

## Cloud Reproduction

These experiments can be reproduced on cloud instances:

**AWS:**
- **Instance Type**: c6i.4xlarge (16 vCPUs, 32 GB RAM)
- **With GPU (ML)**: g5.xlarge (4 vCPUs, 16 GB RAM, A10G GPU)
- **Storage**: 100 GB gp3 SSD
- **Region**: us-east-1
- **OS**: Ubuntu 22.04 AMI

**GCP:**
- **Instance Type**: c2-standard-16 (16 vCPUs, 64 GB RAM)
- **With GPU (ML)**: n1-standard-8 + 1x NVIDIA T4
- **Storage**: 100 GB SSD persistent disk
- **Region**: us-central1

**Azure:**
- **Instance Type**: Standard_F16s_v2 (16 vCPUs, 32 GB RAM)
- **With GPU (ML)**: Standard_NC6s_v3 (6 vCPUs, 112 GB RAM, V100)
- **Storage**: 128 GB Premium SSD
- **Region**: East US

## Cost Estimate

To reproduce all experiments:

- **Local Machine**: ~$2000 hardware (one-time) + $5/month electricity
- **AWS**: ~$10 for all experiments (c6i.4xlarge, ~5 hours)
- **GCP**: ~$12 for all experiments (c2-standard-16, ~5 hours)
- **Azure**: ~$15 for all experiments (F16s_v2, ~5 hours)

**Note**: Core experiments (no ML) can run on free-tier instances (<2 hours).

---

**Last Updated**: January 2026  
**Hardware Configuration Version**: 1.0
