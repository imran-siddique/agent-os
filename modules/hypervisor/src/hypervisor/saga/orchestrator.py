"""
Semantic Saga Orchestrator

Manages multi-step agent transactions with automatic reverse-order
compensation on failure. Integrates with the Reversibility Registry
and Slashing Engine for escalation.
"""

from __future__ import annotations

import uuid
from typing import Any, Callable, Optional

from hypervisor.saga.state_machine import (
    Saga,
    SagaState,
    SagaStateError,
    SagaStep,
    StepState,
)


class SagaOrchestrator:
    """
    Orchestrates multi-step agent transactions with saga semantics.

    Forward execution records each step. On failure, the orchestrator
    iterates the Reversibility Registry in reverse order, calling
    Undo_API for each committed step. If any Undo_API fails,
    Joint Liability slashing is triggered.
    """

    def __init__(self) -> None:
        self._sagas: dict[str, Saga] = {}

    def create_saga(self, session_id: str) -> Saga:
        """Create a new saga for a session."""
        saga = Saga(
            saga_id=f"saga:{uuid.uuid4()}",
            session_id=session_id,
        )
        self._sagas[saga.saga_id] = saga
        return saga

    def add_step(
        self,
        saga_id: str,
        action_id: str,
        agent_did: str,
        execute_api: str,
        undo_api: Optional[str] = None,
        timeout_seconds: int = 300,
    ) -> SagaStep:
        """Add a step to a saga."""
        saga = self._get_saga(saga_id)
        step = SagaStep(
            step_id=f"step:{uuid.uuid4()}",
            action_id=action_id,
            agent_did=agent_did,
            execute_api=execute_api,
            undo_api=undo_api,
            timeout_seconds=timeout_seconds,
        )
        saga.steps.append(step)
        return step

    async def execute_step(
        self,
        saga_id: str,
        step_id: str,
        executor: Callable[..., Any],
    ) -> Any:
        """
        Execute a single saga step.

        Args:
            saga_id: Saga identifier
            step_id: Step identifier
            executor: Async callable that performs the action

        Returns:
            Result from the executor

        Raises:
            SagaStateError: If step is not in PENDING state
        """
        saga = self._get_saga(saga_id)
        step = self._get_step(saga, step_id)

        step.transition(StepState.EXECUTING)
        try:
            result = await executor()
            step.execute_result = result
            step.transition(StepState.COMMITTED)
            return result
        except Exception as e:
            step.error = str(e)
            step.transition(StepState.FAILED)
            raise

    async def compensate(
        self,
        saga_id: str,
        compensator: Callable[[SagaStep], Any],
    ) -> list[SagaStep]:
        """
        Run compensation (rollback) for all committed steps in reverse order.

        Args:
            saga_id: Saga identifier
            compensator: Async callable that takes a SagaStep and calls its Undo_API

        Returns:
            List of steps that failed compensation (empty = full success)
        """
        saga = self._get_saga(saga_id)
        saga.transition(SagaState.COMPENSATING)

        failed_compensations: list[SagaStep] = []

        for step in saga.committed_steps_reversed:
            if not step.undo_api:
                # No undo available — mark as failed
                step.state = StepState.COMPENSATION_FAILED
                step.error = "No Undo_API available"
                failed_compensations.append(step)
                continue

            step.transition(StepState.COMPENSATING)
            try:
                result = await compensator(step)
                step.compensation_result = result
                step.transition(StepState.COMPENSATED)
            except Exception as e:
                step.error = f"Compensation failed: {e}"
                step.transition(StepState.COMPENSATION_FAILED)
                failed_compensations.append(step)

        if failed_compensations:
            saga.transition(SagaState.ESCALATED)
            saga.error = (
                f"{len(failed_compensations)} step(s) failed compensation — "
                "Joint Liability slashing triggered"
            )
        else:
            saga.transition(SagaState.COMPLETED)

        return failed_compensations

    def get_saga(self, saga_id: str) -> Optional[Saga]:
        """Get a saga by ID."""
        return self._sagas.get(saga_id)

    @property
    def active_sagas(self) -> list[Saga]:
        """Get all non-terminal sagas."""
        return [
            s for s in self._sagas.values()
            if s.state in (SagaState.RUNNING, SagaState.COMPENSATING)
        ]

    def _get_saga(self, saga_id: str) -> Saga:
        saga = self._sagas.get(saga_id)
        if not saga:
            raise SagaStateError(f"Saga {saga_id} not found")
        return saga

    def _get_step(self, saga: Saga, step_id: str) -> SagaStep:
        for step in saga.steps:
            if step.step_id == step_id:
                return step
        raise SagaStateError(f"Step {step_id} not found in saga {saga.saga_id}")
