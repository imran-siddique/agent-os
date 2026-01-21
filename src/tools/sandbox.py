"""
Sandbox executor for running generated code safely.
This module provides runtime unit testing capabilities with isolation.
"""
import logging
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SandboxExecutor:
    """
    Execute code in an isolated sandbox environment.
    
    This provides runtime unit testing capabilities to ensure
    generated code works correctly before accepting it.
    """
    
    def __init__(self, timeout_seconds: int = 30, memory_limit_mb: int = 512, use_docker: bool = False):
        """
        Initialize the sandbox executor.
        
        Args:
            timeout_seconds: Maximum execution time
            memory_limit_mb: Maximum memory usage
            use_docker: Whether to use Docker for isolation (recommended for production)
        """
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        self.use_docker = use_docker
        
        logger.info(f"SandboxExecutor initialized (timeout={timeout_seconds}s, docker={use_docker})")
    
    def execute_python(self, code: str, test_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute Python code in the sandbox.
        
        Args:
            code: The Python code to execute
            test_code: Optional test code to run
            
        Returns:
            Dictionary with execution results:
                - success: bool
                - output: stdout
                - error: stderr
                - exit_code: int
        """
        logger.info("Executing Python code in sandbox")
        
        if self.use_docker:
            return self._execute_in_docker(code, test_code, "python")
        else:
            return self._execute_local_python(code, test_code)
    
    def execute(self, code: str) -> Dict[str, Any]:
        """
        Convenience method for executing code with a simpler interface.
        Returns result in format: {'status': 'success'|'error', 'output': str, 'error': str}
        
        Args:
            code: The Python code to execute
            
        Returns:
            Dictionary with execution results:
                - status: 'success' or 'error'
                - output: stdout + stderr
                - error: error message if failed
        """
        result = self.execute_python(code)
        
        return {
            'status': 'success' if result['success'] else 'error',
            'output': result['output'] + result['error'],
            'error': result['error'] if not result['success'] else ''
        }
    
    def _execute_local_python(self, code: str, test_code: Optional[str] = None) -> Dict[str, Any]:
        """Execute Python code locally with timeout."""
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            if test_code:
                f.write("\n\n# Test Code\n")
                f.write(test_code)
            code_file = f.name
        
        try:
            # Execute with timeout
            result = subprocess.run(
                ['python3', code_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            
            success = result.returncode == 0
            
            logger.info(f"Execution {'succeeded' if success else 'failed'}")
            
            return {
                'success': success,
                'output': result.stdout,
                'error': result.stderr,
                'exit_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Execution timed out after {self.timeout_seconds}s")
            return {
                'success': False,
                'output': '',
                'error': f'Execution timed out after {self.timeout_seconds} seconds',
                'exit_code': -1
            }
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'exit_code': -1
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(code_file)
            except (OSError, PermissionError) as e:
                logger.warning(f"Failed to delete temporary file {code_file}: {e}")
    
    def _execute_in_docker(self, code: str, test_code: Optional[str], language: str) -> Dict[str, Any]:
        """
        Execute code in a Docker container for better isolation.
        
        TODO: Implement Docker-based execution for production use.
        """
        logger.warning("Docker execution not yet implemented, falling back to local")
        return self._execute_local_python(code, test_code)
    
    def validate_test_cases(self, solution_code: str, test_cases: str) -> bool:
        """
        Validate that test cases pass for the given solution.
        
        Args:
            solution_code: The solution code
            test_cases: Test code to validate
            
        Returns:
            True if all tests pass, False otherwise
        """
        result = self.execute_python(solution_code, test_cases)
        return result['success']


# Alias for compatibility
Sandbox = SandboxExecutor
