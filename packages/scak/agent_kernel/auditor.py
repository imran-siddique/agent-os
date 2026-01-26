"""
Auditor - Simplified reference implementation for soft failure detection.

This is a reference implementation showing the core concept of detecting
"soft failures" (laziness) where agents give up without trying hard enough.

The production implementation is in completeness_auditor.py, which includes
more sophisticated features like differential auditing and teacher model integration.
"""

class CompletenessAuditor:
    def __init__(self):
        # Trigger words that suggest the agent gave up
        self.lazy_signals = [
            "i cannot", "i'm sorry", "no data found", 
            "unable to access", "context does not contain"
        ]

    def audit_response(self, agent_response, tool_output):
        """
        returns: needs_intervention (bool)
        """
        # 1. Check for verbal resignation
        if any(sig in agent_response.lower() for sig in self.lazy_signals):
            return True
        
        # 2. Check for "Empty Success" (Tool worked, but returned nothing)
        if tool_output and len(tool_output) < 10: # e.g. "[]" or ""
            return True
            
        return False
