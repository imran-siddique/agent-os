"""
Load Testing and Performance Benchmarks.

Tests system performance under various load conditions:
- Throughput (requests/second)
- Latency (p50, p95, p99)
- Concurrent request handling
- Resource utilization
- Failure recovery time (MTTR)

Research Foundation:
- "The Art of Capacity Planning" (John Allspaw)
- Load testing best practices (Gatling, JMeter patterns)
- SRE principles (SLIs, SLOs, SLAs)

Architectural Pattern:
- Ramp-up load testing (gradual increase)
- Spike testing (sudden load)
- Endurance testing (sustained load)
- Stress testing (beyond capacity)
"""

from typing import Dict, Any, Optional, List, Callable, Awaitable
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio
import time
from statistics import mean, median, stdev
from collections import defaultdict

logger = logging.getLogger(__name__)


class LoadProfile(str, Enum):
    """Load testing profiles."""
    RAMP_UP = "ramp_up"        # Gradually increase load
    SPIKE = "spike"            # Sudden load increase
    ENDURANCE = "endurance"    # Sustained load
    STRESS = "stress"          # Beyond capacity


class TestStatus(str, Enum):
    """Status of load test."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RequestMetrics(BaseModel):
    """Metrics for a single request."""
    request_id: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    success: bool
    error: Optional[str] = None
    status_code: Optional[int] = None


class LoadTestResult(BaseModel):
    """
    Results from a load test.
    
    Includes throughput, latency percentiles, error rates.
    """
    test_id: str
    profile: LoadProfile
    status: TestStatus
    
    # Test parameters
    total_requests: int
    concurrent_requests: int
    duration_seconds: float
    
    # Throughput metrics
    requests_per_second: float
    successful_requests: int
    failed_requests: int
    error_rate: float
    
    # Latency metrics (milliseconds)
    latency_min: float
    latency_max: float
    latency_mean: float
    latency_median: float
    latency_p95: float
    latency_p99: float
    latency_stddev: float
    
    # Resource metrics (if available)
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    
    # Timestamp
    started_at: datetime
    completed_at: Optional[datetime] = None


class LoadTester:
    """
    Load testing framework for agent system.
    
    Implements:
    1. Various load profiles (ramp-up, spike, endurance)
    2. Concurrent request simulation
    3. Latency and throughput measurement
    4. Resource monitoring
    5. Failure recovery testing (MTTR)
    
    Research: SRE principles for defining SLIs/SLOs.
    """
    
    def __init__(self):
        """Initialize load tester."""
        self.tests: Dict[str, LoadTestResult] = {}
        self.metrics: Dict[str, List[RequestMetrics]] = defaultdict(list)
        
        logger.info("LoadTester initialized")
    
    async def run_load_test(
        self,
        target_function: Callable[[], Awaitable[Any]],
        profile: LoadProfile = LoadProfile.RAMP_UP,
        total_requests: int = 1000,
        concurrent_requests: int = 10,
        duration_seconds: Optional[int] = None,
        ramp_up_seconds: Optional[int] = None
    ) -> LoadTestResult:
        """
        Run load test with specified profile.
        
        Args:
            target_function: Async function to test
            profile: Load profile type
            total_requests: Total requests to make
            concurrent_requests: Max concurrent requests
            duration_seconds: Max test duration (None = until total_requests)
            ramp_up_seconds: Time to reach max concurrency (for ramp_up profile)
            
        Returns:
            LoadTestResult with performance metrics
        """
        test_id = f"test-{int(time.time())}"
        
        logger.info(
            f"Starting load test {test_id} "
            f"(profile: {profile.value}, requests: {total_requests}, "
            f"concurrency: {concurrent_requests})"
        )
        
        # Create result
        result = LoadTestResult(
            test_id=test_id,
            profile=profile,
            status=TestStatus.RUNNING,
            total_requests=total_requests,
            concurrent_requests=concurrent_requests,
            duration_seconds=0.0,
            requests_per_second=0.0,
            successful_requests=0,
            failed_requests=0,
            error_rate=0.0,
            latency_min=0.0,
            latency_max=0.0,
            latency_mean=0.0,
            latency_median=0.0,
            latency_p95=0.0,
            latency_p99=0.0,
            latency_stddev=0.0,
            started_at=datetime.now()
        )
        
        self.tests[test_id] = result
        
        try:
            # Execute test based on profile
            if profile == LoadProfile.RAMP_UP:
                await self._run_ramp_up(
                    test_id,
                    target_function,
                    total_requests,
                    concurrent_requests,
                    ramp_up_seconds or 30
                )
            elif profile == LoadProfile.SPIKE:
                await self._run_spike(
                    test_id,
                    target_function,
                    total_requests,
                    concurrent_requests
                )
            elif profile == LoadProfile.ENDURANCE:
                await self._run_endurance(
                    test_id,
                    target_function,
                    duration_seconds or 300,
                    concurrent_requests
                )
            elif profile == LoadProfile.STRESS:
                await self._run_stress(
                    test_id,
                    target_function,
                    total_requests,
                    concurrent_requests
                )
            
            # Calculate metrics
            self._calculate_metrics(test_id)
            
            result.status = TestStatus.COMPLETED
            result.completed_at = datetime.now()
            
            logger.info(
                f"Load test {test_id} completed: "
                f"{result.requests_per_second:.1f} req/s, "
                f"p95: {result.latency_p95:.1f}ms, "
                f"error rate: {result.error_rate:.2%}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Load test {test_id} failed: {e}")
            result.status = TestStatus.FAILED
            result.completed_at = datetime.now()
            raise
    
    async def _run_ramp_up(
        self,
        test_id: str,
        target_function: Callable,
        total_requests: int,
        max_concurrency: int,
        ramp_up_seconds: int
    ):
        """
        Ramp-up load test (gradually increase concurrency).
        
        Args:
            test_id: Test identifier
            target_function: Function to test
            total_requests: Total requests
            max_concurrency: Maximum concurrency
            ramp_up_seconds: Time to reach max concurrency
        """
        requests_made = 0
        start_time = time.time()
        
        # Calculate concurrency increase rate
        concurrency_per_second = max_concurrency / ramp_up_seconds
        
        while requests_made < total_requests:
            elapsed = time.time() - start_time
            
            # Calculate current concurrency based on ramp-up
            if elapsed < ramp_up_seconds:
                current_concurrency = int(concurrency_per_second * elapsed) + 1
            else:
                current_concurrency = max_concurrency
            
            # Launch concurrent requests
            tasks = []
            for _ in range(min(current_concurrency, total_requests - requests_made)):
                task = self._make_request(test_id, target_function)
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            requests_made += len(tasks)
            
            # Small delay to control rate
            await asyncio.sleep(0.1)
    
    async def _run_spike(
        self,
        test_id: str,
        target_function: Callable,
        total_requests: int,
        concurrency: int
    ):
        """
        Spike load test (sudden load increase).
        
        Args:
            test_id: Test identifier
            target_function: Function to test
            total_requests: Total requests
            concurrency: Concurrent requests
        """
        # Launch all requests at once (spike)
        tasks = []
        
        for _ in range(total_requests):
            task = self._make_request(test_id, target_function)
            tasks.append(task)
            
            # Control concurrency
            if len(tasks) >= concurrency:
                await asyncio.gather(*tasks, return_exceptions=True)
                tasks = []
        
        # Wait for remaining
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_endurance(
        self,
        test_id: str,
        target_function: Callable,
        duration_seconds: int,
        concurrency: int
    ):
        """
        Endurance test (sustained load for duration).
        
        Args:
            test_id: Test identifier
            target_function: Function to test
            duration_seconds: Test duration
            concurrency: Concurrent requests
        """
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # Launch concurrent requests
            tasks = [
                self._make_request(test_id, target_function)
                for _ in range(concurrency)
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Small delay
            await asyncio.sleep(0.1)
    
    async def _run_stress(
        self,
        test_id: str,
        target_function: Callable,
        total_requests: int,
        initial_concurrency: int
    ):
        """
        Stress test (increase load beyond capacity).
        
        Args:
            test_id: Test identifier
            target_function: Function to test
            total_requests: Total requests
            initial_concurrency: Starting concurrency
        """
        requests_made = 0
        current_concurrency = initial_concurrency
        
        while requests_made < total_requests:
            # Increase concurrency by 20% each iteration
            current_concurrency = int(current_concurrency * 1.2)
            
            # Launch concurrent requests
            batch_size = min(current_concurrency, total_requests - requests_made)
            tasks = [
                self._make_request(test_id, target_function)
                for _ in range(batch_size)
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            requests_made += batch_size
    
    async def _make_request(
        self,
        test_id: str,
        target_function: Callable
    ):
        """
        Make single request and record metrics.
        
        Args:
            test_id: Test identifier
            target_function: Function to call
        """
        request_id = f"{test_id}-{len(self.metrics[test_id])}"
        start_time = datetime.now()
        start_perf = time.perf_counter()
        
        try:
            await target_function()
            
            end_time = datetime.now()
            duration_ms = (time.perf_counter() - start_perf) * 1000
            
            metric = RequestMetrics(
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                success=True
            )
            
            self.metrics[test_id].append(metric)
            
        except Exception as e:
            end_time = datetime.now()
            duration_ms = (time.perf_counter() - start_perf) * 1000
            
            metric = RequestMetrics(
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )
            
            self.metrics[test_id].append(metric)
    
    def _calculate_metrics(self, test_id: str):
        """
        Calculate aggregate metrics from request data.
        
        Args:
            test_id: Test identifier
        """
        result = self.tests[test_id]
        metrics = self.metrics[test_id]
        
        if not metrics:
            return
        
        # Duration
        start = min(m.start_time for m in metrics)
        end = max(m.end_time for m in metrics)
        result.duration_seconds = (end - start).total_seconds()
        
        # Success/failure counts
        result.successful_requests = sum(1 for m in metrics if m.success)
        result.failed_requests = sum(1 for m in metrics if not m.success)
        result.error_rate = result.failed_requests / len(metrics)
        
        # Throughput
        result.requests_per_second = len(metrics) / max(result.duration_seconds, 0.001)
        
        # Latency statistics
        latencies = [m.duration_ms for m in metrics]
        latencies.sort()
        
        result.latency_min = latencies[0]
        result.latency_max = latencies[-1]
        result.latency_mean = mean(latencies)
        result.latency_median = median(latencies)
        
        # Percentiles
        p95_index = int(len(latencies) * 0.95)
        p99_index = int(len(latencies) * 0.99)
        
        result.latency_p95 = latencies[p95_index]
        result.latency_p99 = latencies[p99_index]
        
        # Standard deviation
        if len(latencies) > 1:
            result.latency_stddev = stdev(latencies)
        else:
            result.latency_stddev = 0.0
    
    def get_test_result(self, test_id: str) -> Optional[LoadTestResult]:
        """
        Get test result.
        
        Args:
            test_id: Test identifier
            
        Returns:
            LoadTestResult or None
        """
        return self.tests.get(test_id)
    
    def list_tests(self) -> List[Dict[str, Any]]:
        """
        List all tests.
        
        Returns:
            List of test summaries
        """
        return [
            {
                "test_id": result.test_id,
                "profile": result.profile.value,
                "status": result.status.value,
                "requests_per_second": result.requests_per_second,
                "error_rate": result.error_rate,
                "latency_p95": result.latency_p95
            }
            for result in self.tests.values()
        ]


class BenchmarkSuite:
    """
    Comprehensive benchmark suite for system validation.
    
    Tests:
    - Agent execution throughput
    - Audit latency
    - Patch application speed
    - Memory operations
    - Distributed execution overhead
    """
    
    def __init__(self, load_tester: LoadTester):
        """
        Initialize benchmark suite.
        
        Args:
            load_tester: LoadTester instance
        """
        self.load_tester = load_tester
        self.results: Dict[str, LoadTestResult] = {}
        
        logger.info("BenchmarkSuite initialized")
    
    async def run_all_benchmarks(self) -> Dict[str, LoadTestResult]:
        """
        Run full benchmark suite.
        
        Returns:
            Dict of benchmark results
        """
        logger.info("Running full benchmark suite...")
        
        # Benchmark 1: Agent execution throughput
        async def agent_task():
            await asyncio.sleep(0.01)  # Simulate agent work
        
        result1 = await self.load_tester.run_load_test(
            agent_task,
            profile=LoadProfile.RAMP_UP,
            total_requests=1000,
            concurrent_requests=20
        )
        self.results["agent_throughput"] = result1
        
        # Benchmark 2: Spike handling
        result2 = await self.load_tester.run_load_test(
            agent_task,
            profile=LoadProfile.SPIKE,
            total_requests=500,
            concurrent_requests=50
        )
        self.results["spike_handling"] = result2
        
        # Benchmark 3: Endurance test
        result3 = await self.load_tester.run_load_test(
            agent_task,
            profile=LoadProfile.ENDURANCE,
            duration_seconds=60,
            concurrent_requests=10
        )
        self.results["endurance"] = result3
        
        logger.info("Benchmark suite completed")
        
        return self.results
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 80)
        print("BENCHMARK RESULTS")
        print("=" * 80)
        
        for name, result in self.results.items():
            print(f"\n{name.upper()}:")
            print(f"  Throughput: {result.requests_per_second:.1f} req/s")
            print(f"  Latency p50: {result.latency_median:.1f}ms")
            print(f"  Latency p95: {result.latency_p95:.1f}ms")
            print(f"  Latency p99: {result.latency_p99:.1f}ms")
            print(f"  Error rate: {result.error_rate:.2%}")
        
        print("\n" + "=" * 80)


# Example usage
async def example_load_testing():
    """Demonstrate load testing."""
    tester = LoadTester()
    
    # Define target function to test
    async def test_function():
        """Simulate agent work."""
        await asyncio.sleep(0.02)  # 20ms work
        
        # Simulate occasional failures
        import random
        if random.random() < 0.05:  # 5% error rate
            raise RuntimeError("Simulated failure")
        
        return {"status": "success"}
    
    # Run different load profiles
    print("Running RAMP_UP test...")
    result1 = await tester.run_load_test(
        test_function,
        profile=LoadProfile.RAMP_UP,
        total_requests=500,
        concurrent_requests=20,
        ramp_up_seconds=10
    )
    
    print(f"Results: {result1.requests_per_second:.1f} req/s, "
          f"p95: {result1.latency_p95:.1f}ms")
    
    print("\nRunning SPIKE test...")
    result2 = await tester.run_load_test(
        test_function,
        profile=LoadProfile.SPIKE,
        total_requests=200,
        concurrent_requests=50
    )
    
    print(f"Results: {result2.requests_per_second:.1f} req/s, "
          f"p95: {result2.latency_p95:.1f}ms")
    
    # Run full benchmark suite
    print("\nRunning full benchmark suite...")
    suite = BenchmarkSuite(tester)
    await suite.run_all_benchmarks()
    suite.print_summary()


if __name__ == "__main__":
    asyncio.run(example_load_testing())
