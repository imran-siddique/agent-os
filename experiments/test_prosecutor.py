# experiments/test_prosecutor.py
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cross_model_verification_kernel.agents.verifier_gemini import GeminiVerifier
from cross_model_verification_kernel.tools.sandbox import Sandbox

# 1. The Suspect: A Fibonacci function that crashes on negative numbers
# Using restrictive conditions (== 0, == 1) instead of (<= 1) causes infinite recursion
buggy_code = """
def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n-1) + fibonacci(n-2)
"""

# 2. The Prosecutor
verifier = GeminiVerifier()
sandbox = Sandbox()

print("--- STARTING PROSECUTOR TEST ---")
print("Target: Buggy Fibonacci (Infinite recursion on negatives)")

# 3. Generate Attack
attack_code = verifier.generate_hostile_test(buggy_code)
print(f"\n[Generated Attack Code]\n{attack_code}")

# 4. Execute
full_script = f"{buggy_code}\n{attack_code}"
result = sandbox.execute(full_script)

print(f"\n[Sandbox Result] {result['status']}")
if result["status"] == "error":
    print("SUCCESS: The Prosecutor successfully caught the bug!")
    print(f"Traceback: {result['output'][:300]}")
else:
    print("FAILURE: The buggy code survived.")
