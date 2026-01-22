# src/core/trace_logger.py
"""
The Witness: Serializes the entire debate into a JSON evidence file.

This module provides traceability for research purposes, allowing us to log
the exact moment one model catches another's error and how it was fixed.
"""
import json
import os
import time
from dataclasses import asdict
from typing import Any
from cross_model_verification_kernel.core.types import NodeState


class TraceLogger:
    """
    The Witness: Serializes the entire debate into a JSON evidence file.
    
    This logger handles the JSON conversion of NodeState dataclasses,
    providing clean artifacts for supplementary material in research papers.
    """
    
    def __init__(self, log_dir: str = "logs/traces"):
        """
        Initialize the TraceLogger.
        
        Args:
            log_dir: Directory to save trace files (default: "logs/traces")
        """
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def save_trace(self, filename_prefix: str, state: NodeState) -> str:
        """
        Save the NodeState to a JSON file.
        
        Args:
            filename_prefix: Prefix for the filename (e.g., "experiment", "cmvk_prob_001")
            state: The NodeState containing the complete history
            
        Returns:
            str: Path to the saved trace file
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = os.path.join(self.log_dir, filename)

        # Convert dataclass to dict
        data = asdict(state)
        
        # Add metadata for the paper
        data["meta"] = {
            "timestamp": timestamp,
            "total_attempts": len(state.history),
            "final_status": "solved" if any(t['status'] == 'success' for t in data['history']) else "failed"
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"📝 Trace saved to: {filepath}")
        return filepath
