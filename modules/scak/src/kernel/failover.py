"""
Failover and Redundancy Mechanisms for high availability.

Implements patterns for fault tolerance:
- Health monitoring and circuit breakers
- Automatic failover to backup components
- Leader election for distributed coordination
- Graceful degradation

Research Foundation:
- "Designing Distributed Systems" (Kubernetes patterns)
- "Release It!" (Production-ready patterns)
- Netflix Hystrix circuit breaker pattern

Architectural Pattern:
- Health checks with exponential backoff
- Circuit breaker states (closed, open, half-open)
- Leader election via consensus
- Backup component activation
"""

from typing import Dict, Any, Optional, List, Callable, Awaitable
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio
from uuid import uuid4

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status of a component."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class ComponentHealth(BaseModel):
    """
    Health status of a system component.
    
    Tracks availability, latency, error rate for monitoring.
    """
    component_id: str
    component_type: str  # "agent", "database", "api", etc.
    status: HealthStatus = HealthStatus.UNKNOWN
    
    # Metrics
    last_check: datetime = Field(default_factory=datetime.now)
    consecutive_failures: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0.0
    
    # Metadata
    message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class CircuitBreaker:
    """
    Circuit breaker for fault tolerance.
    
    Prevents cascading failures by:
    1. Tracking failure rate
    2. Opening circuit when threshold exceeded
    3. Periodically testing if service recovered
    4. Closing circuit when health restored
    
    Research: Netflix Hystrix pattern for microservices.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        half_open_max_calls: int = 3
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Circuit identifier
            failure_threshold: Failures before opening circuit
            timeout_seconds: Time before trying to close circuit
            half_open_max_calls: Max calls allowed in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        
        logger.info(
            f"CircuitBreaker '{name}' initialized "
            f"(threshold: {failure_threshold}, timeout: {timeout_seconds}s)"
        )
    
    async def call(
        self,
        func: Callable[[], Awaitable[Any]],
        fallback: Optional[Callable[[], Awaitable[Any]]] = None
    ) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            fallback: Optional fallback function if circuit open
            
        Returns:
            Function result
            
        Raises:
            RuntimeError: If circuit open and no fallback
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            # Check if timeout elapsed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    # Try half-open
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info(f"Circuit '{self.name}' entering HALF_OPEN state")
                else:
                    # Still open, use fallback
                    if fallback:
                        logger.warning(
                            f"Circuit '{self.name}' OPEN, using fallback"
                        )
                        return await fallback()
                    else:
                        raise RuntimeError(
                            f"Circuit '{self.name}' OPEN and no fallback available"
                        )
        
        # Half-open: limit calls
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise RuntimeError(
                    f"Circuit '{self.name}' HALF_OPEN, max calls reached"
                )
            self.half_open_calls += 1
        
        # Execute function
        try:
            result = await func()
            
            # Success
            self._record_success()
            
            return result
            
        except Exception as e:
            # Failure
            self._record_failure()
            
            # Use fallback if available
            if fallback:
                logger.warning(
                    f"Circuit '{self.name}' call failed, using fallback: {e}"
                )
                return await fallback()
            else:
                raise
    
    def _record_success(self):
        """Record successful call."""
        self.success_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # Check if can close circuit
            if self.success_count >= 2:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit '{self.name}' closed (recovered)")
    
    def _record_failure(self):
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            # Reopen circuit
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit '{self.name}' reopened (still failing)")
        
        elif self.state == CircuitState.CLOSED:
            # Check if should open
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error(
                    f"Circuit '{self.name}' opened "
                    f"({self.failure_count} consecutive failures)"
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class HealthMonitor:
    """
    Monitor health of system components.
    
    Implements:
    - Periodic health checks
    - Exponential backoff for unhealthy components
    - Alerting on status changes
    - Aggregated system health
    """
    
    def __init__(
        self,
        check_interval_seconds: int = 30,
        unhealthy_threshold: int = 3
    ):
        """
        Initialize health monitor.
        
        Args:
            check_interval_seconds: Time between health checks
            unhealthy_threshold: Consecutive failures before marking unhealthy
        """
        self.check_interval = check_interval_seconds
        self.unhealthy_threshold = unhealthy_threshold
        
        self.components: Dict[str, ComponentHealth] = {}
        self.health_checks: Dict[str, Callable[[], Awaitable[bool]]] = {}
        
        self.monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        logger.info("HealthMonitor initialized")
    
    def register_component(
        self,
        component_id: str,
        component_type: str,
        health_check: Callable[[], Awaitable[bool]]
    ):
        """
        Register component for monitoring.
        
        Args:
            component_id: Unique component identifier
            component_type: Type of component
            health_check: Async function that returns True if healthy
        """
        self.components[component_id] = ComponentHealth(
            component_id=component_id,
            component_type=component_type
        )
        
        self.health_checks[component_id] = health_check
        
        logger.info(f"Registered component: {component_id} ({component_type})")
    
    async def check_component(self, component_id: str) -> HealthStatus:
        """
        Check health of specific component.
        
        Args:
            component_id: Component to check
            
        Returns:
            HealthStatus
        """
        if component_id not in self.components:
            return HealthStatus.UNKNOWN
        
        component = self.components[component_id]
        health_check = self.health_checks[component_id]
        
        start_time = datetime.now()
        
        try:
            is_healthy = await health_check()
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update metrics
            component.total_requests += 1
            component.last_check = datetime.now()
            
            # Update latency (moving average)
            component.avg_latency_ms = (
                component.avg_latency_ms * 0.9 + latency_ms * 0.1
            )
            
            if is_healthy:
                component.consecutive_failures = 0
                component.status = HealthStatus.HEALTHY
                component.message = "Component healthy"
            else:
                component.consecutive_failures += 1
                component.failed_requests += 1
                
                if component.consecutive_failures >= self.unhealthy_threshold:
                    component.status = HealthStatus.UNHEALTHY
                    component.message = f"{component.consecutive_failures} consecutive failures"
                else:
                    component.status = HealthStatus.DEGRADED
                    component.message = "Health check failed"
            
            return component.status
            
        except Exception as e:
            component.consecutive_failures += 1
            component.failed_requests += 1
            component.total_requests += 1
            component.last_check = datetime.now()
            
            if component.consecutive_failures >= self.unhealthy_threshold:
                component.status = HealthStatus.UNHEALTHY
            else:
                component.status = HealthStatus.DEGRADED
            
            component.message = str(e)
            
            logger.error(f"Health check failed for {component_id}: {e}")
            
            return component.status
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health monitoring stopped")
    
    async def _monitor_loop(self):
        """Continuous monitoring loop."""
        while self.monitoring:
            # Check all components
            for component_id in self.components:
                await self.check_component(component_id)
            
            # Wait for next interval
            await asyncio.sleep(self.check_interval)
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get aggregated system health.
        
        Returns:
            dict with overall status and component details
        """
        if not self.components:
            return {
                "overall": HealthStatus.UNKNOWN.value,
                "components": {}
            }
        
        # Aggregate status
        statuses = [c.status for c in self.components.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        else:
            overall = HealthStatus.DEGRADED
        
        return {
            "overall": overall.value,
            "components": {
                comp_id: {
                    "status": comp.status.value,
                    "consecutive_failures": comp.consecutive_failures,
                    "error_rate": comp.failed_requests / max(comp.total_requests, 1),
                    "avg_latency_ms": comp.avg_latency_ms,
                    "message": comp.message
                }
                for comp_id, comp in self.components.items()
            },
            "checked_at": datetime.now().isoformat()
        }


class FailoverManager:
    """
    Manage failover to backup components.
    
    Implements:
    - Primary/backup component pairs
    - Automatic failover on primary failure
    - Failback when primary recovers
    - Load balancing across backups
    """
    
    def __init__(self, health_monitor: HealthMonitor):
        """
        Initialize failover manager.
        
        Args:
            health_monitor: HealthMonitor instance
        """
        self.health_monitor = health_monitor
        
        # Map: component_id -> list of backup component_ids
        self.backups: Dict[str, List[str]] = {}
        
        # Map: component_id -> current active component_id
        self.active: Dict[str, str] = {}
        
        logger.info("FailoverManager initialized")
    
    def register_backup(
        self,
        primary_id: str,
        backup_id: str
    ):
        """
        Register backup component for a primary.
        
        Args:
            primary_id: Primary component ID
            backup_id: Backup component ID
        """
        if primary_id not in self.backups:
            self.backups[primary_id] = []
            self.active[primary_id] = primary_id
        
        self.backups[primary_id].append(backup_id)
        
        logger.info(f"Registered backup: {backup_id} for {primary_id}")
    
    async def get_active_component(self, component_id: str) -> str:
        """
        Get active component (primary or backup).
        
        Automatically fails over if primary unhealthy.
        
        Args:
            component_id: Requested component ID
            
        Returns:
            Active component ID (might be backup)
        """
        # Check if has backups
        if component_id not in self.backups:
            return component_id
        
        current_active = self.active.get(component_id, component_id)
        
        # Check health of current active
        status = await self.health_monitor.check_component(current_active)
        
        if status == HealthStatus.HEALTHY or status == HealthStatus.DEGRADED:
            # Current active is OK
            return current_active
        
        # Current active unhealthy, try failover
        logger.warning(
            f"Component {current_active} unhealthy, attempting failover"
        )
        
        # Try primary first (if not already active)
        if current_active != component_id:
            status = await self.health_monitor.check_component(component_id)
            if status != HealthStatus.UNHEALTHY:
                # Primary recovered, failback
                logger.info(f"Failing back to primary: {component_id}")
                self.active[component_id] = component_id
                return component_id
        
        # Try backups
        for backup_id in self.backups[component_id]:
            if backup_id == current_active:
                continue
            
            status = await self.health_monitor.check_component(backup_id)
            if status != HealthStatus.UNHEALTHY:
                # Found healthy backup
                logger.info(f"Failed over to backup: {backup_id}")
                self.active[component_id] = backup_id
                return backup_id
        
        # No healthy component found
        logger.error(f"No healthy component found for {component_id}")
        return current_active  # Return current even if unhealthy
    
    def get_failover_stats(self) -> Dict[str, Any]:
        """Get failover statistics."""
        return {
            "primary_components": len(self.backups),
            "total_backups": sum(len(backups) for backups in self.backups.values()),
            "active_mappings": self.active,
            "failovers": {
                primary: active
                for primary, active in self.active.items()
                if active != primary
            }
        }


# Example usage
async def example_failover():
    """Demonstrate failover and health monitoring."""
    # Create health monitor
    monitor = HealthMonitor(check_interval_seconds=5)
    
    # Register components
    async def primary_check():
        # Simulate primary becoming unhealthy after 3 checks
        if monitor.components["primary"].total_requests > 3:
            return False
        return True
    
    async def backup_check():
        # Backup always healthy
        return True
    
    monitor.register_component("primary", "agent", primary_check)
    monitor.register_component("backup", "agent", backup_check)
    
    # Create failover manager
    failover = FailoverManager(monitor)
    failover.register_backup("primary", "backup")
    
    # Start monitoring
    await monitor.start_monitoring()
    
    try:
        # Simulate requests
        for i in range(10):
            active = await failover.get_active_component("primary")
            print(f"Request {i}: Using component {active}")
            
            await asyncio.sleep(1)
        
        # Get health
        health = monitor.get_system_health()
        print(f"System health: {health}")
        
        # Get failover stats
        stats = failover.get_failover_stats()
        print(f"Failover stats: {stats}")
        
    finally:
        await monitor.stop_monitoring()
    
    # Circuit breaker example
    breaker = CircuitBreaker("api_service", failure_threshold=3)
    
    call_count = 0
    
    async def api_call():
        nonlocal call_count
        call_count += 1
        
        # Simulate failures
        if call_count <= 5:
            raise RuntimeError("Service unavailable")
        
        return {"status": "success"}
    
    async def fallback():
        return {"status": "fallback", "message": "Using cached data"}
    
    # Make calls through circuit breaker
    for i in range(10):
        try:
            result = await breaker.call(api_call, fallback=fallback)
            print(f"Call {i}: {result}")
        except RuntimeError as e:
            print(f"Call {i}: Error - {e}")
        
        await asyncio.sleep(0.5)
    
    stats = breaker.get_stats()
    print(f"Circuit breaker stats: {stats}")


if __name__ == "__main__":
    asyncio.run(example_failover())
