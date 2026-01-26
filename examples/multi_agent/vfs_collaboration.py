"""
Multi-Agent Collaboration with Virtual File System

Demonstrates how multiple SDLC agents can collaborate on a shared codebase
using CaaS Virtual File System. Each agent can create, read, update files,
and all agents see each other's changes in real-time.

Scenario:
- Developer Agent: Creates initial code files
- Reviewer Agent: Reviews code and suggests improvements
- Documenter Agent: Adds documentation based on code
- Tester Agent: Creates tests for the code

All agents work on the same shared VFS instance, demonstrating true
multi-agent collaboration on project state.
"""

import sys
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from caas import VirtualFileSystem, FileType


class BaseAgent:
    """Base class for all SDLC agents."""
    
    def __init__(self, agent_id: str, role: str, vfs: VirtualFileSystem):
        self.agent_id = agent_id
        self.role = role
        self.vfs = vfs
        print(f"\n{'='*70}")
        print(f"🤖 {role} Agent ({agent_id}) initialized")
        print(f"{'='*70}")
    
    def log(self, message: str):
        """Log a message from this agent."""
        print(f"[{self.role}] {message}")


class DeveloperAgent(BaseAgent):
    """Agent that writes code."""
    
    def __init__(self, vfs: VirtualFileSystem):
        super().__init__("developer-1", "Developer", vfs)
    
    def create_project_structure(self):
        """Create initial project structure."""
        self.log("Creating project structure...")
        
        # Create main module
        self.vfs.create_file(
            path="/project/calculator.py",
            content="""class Calculator:
    \"\"\"A simple calculator class.\"\"\"
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
""",
            agent_id=self.agent_id,
            metadata={"language": "python", "module": "calculator"}
        )
        
        # Create utils module
        self.vfs.create_file(
            path="/project/utils.py",
            content="""def format_result(value, decimals=2):
    \"\"\"Format a numeric result for display.\"\"\"
    return f"{value:.{decimals}f}"

def validate_number(value):
    \"\"\"Validate that a value is a number.\"\"\"
    if not isinstance(value, (int, float)):
        raise TypeError(f"Expected number, got {type(value).__name__}")
    return True
""",
            agent_id=self.agent_id,
            metadata={"language": "python", "module": "utils"}
        )
        
        self.log("✓ Created calculator.py")
        self.log("✓ Created utils.py")


class ReviewerAgent(BaseAgent):
    """Agent that reviews code and suggests improvements."""
    
    def __init__(self, vfs: VirtualFileSystem):
        super().__init__("reviewer-1", "Code Reviewer", vfs)
    
    def review_code(self):
        """Review code and add improvements."""
        self.log("Reviewing code...")
        
        # Read calculator.py
        calc_code = self.vfs.read_file("/project/calculator.py")
        self.log(f"✓ Read calculator.py ({len(calc_code)} chars)")
        
        # Add type hints and improve error handling
        improved_code = '''from typing import Union

class Calculator:
    """A simple calculator class with type hints and error handling."""
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Divide a by b.
        
        Raises:
            ValueError: If b is zero.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
'''
        
        self.vfs.update_file(
            path="/project/calculator.py",
            content=improved_code,
            agent_id=self.agent_id,
            message="Add type hints and improve documentation"
        )
        
        self.log("✓ Updated calculator.py with type hints")
        self.log("✓ Improved error handling documentation")


class DocumenterAgent(BaseAgent):
    """Agent that writes documentation."""
    
    def __init__(self, vfs: VirtualFileSystem):
        super().__init__("documenter-1", "Documentation", vfs)
    
    def create_documentation(self):
        """Create documentation files."""
        self.log("Creating documentation...")
        
        # Read the code to understand what to document
        calc_code = self.vfs.read_file("/project/calculator.py")
        utils_code = self.vfs.read_file("/project/utils.py")
        
        self.log(f"✓ Analyzed calculator.py")
        self.log(f"✓ Analyzed utils.py")
        
        # Create README
        self.vfs.create_file(
            path="/project/README.md",
            content="""# Calculator Project

A simple calculator implementation in Python with type hints and comprehensive error handling.

## Features

- Basic arithmetic operations (add, subtract, multiply, divide)
- Type hints for better IDE support
- Comprehensive error handling
- Utility functions for formatting and validation

## Usage

```python
from calculator import Calculator

calc = Calculator()
result = calc.add(5, 3)
print(f"5 + 3 = {result}")  # Output: 5 + 3 = 8
```

## Modules

- `calculator.py`: Core calculator implementation
- `utils.py`: Utility functions for formatting and validation
- `test_calculator.py`: Test suite (if available)

## Development

This project was collaboratively developed using CaaS Virtual File System,
allowing multiple SDLC agents to work together seamlessly.

### Contributors

- Developer Agent: Initial implementation
- Code Reviewer Agent: Type hints and documentation improvements
- Documentation Agent: README and API documentation
- Testing Agent: Test suite implementation
""",
            agent_id=self.agent_id,
            metadata={"type": "documentation"}
        )
        
        self.log("✓ Created README.md")
        self.log("✓ Documented all modules")


class TesterAgent(BaseAgent):
    """Agent that creates tests."""
    
    def __init__(self, vfs: VirtualFileSystem):
        super().__init__("tester-1", "Test Engineer", vfs)
    
    def create_tests(self):
        """Create test files."""
        self.log("Creating test suite...")
        
        # Read the code to understand what to test
        calc_code = self.vfs.read_file("/project/calculator.py")
        self.log("✓ Analyzed code for test coverage")
        
        # Create test file
        self.vfs.create_file(
            path="/project/test_calculator.py",
            content="""import pytest
from calculator import Calculator

class TestCalculator:
    \"\"\"Test suite for Calculator class.\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures.\"\"\"
        self.calc = Calculator()
    
    def test_add(self):
        \"\"\"Test addition.\"\"\"
        assert self.calc.add(2, 3) == 5
        assert self.calc.add(-1, 1) == 0
        assert self.calc.add(0, 0) == 0
    
    def test_subtract(self):
        \"\"\"Test subtraction.\"\"\"
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(0, 5) == -5
    
    def test_multiply(self):
        \"\"\"Test multiplication.\"\"\"
        assert self.calc.multiply(3, 4) == 12
        assert self.calc.multiply(-2, 3) == -6
        assert self.calc.multiply(0, 100) == 0
    
    def test_divide(self):
        \"\"\"Test division.\"\"\"
        assert self.calc.divide(10, 2) == 5
        assert self.calc.divide(7, 2) == 3.5
    
    def test_divide_by_zero(self):
        \"\"\"Test division by zero raises error.\"\"\"
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.calc.divide(10, 0)
""",
            agent_id=self.agent_id,
            metadata={"type": "test", "framework": "pytest"}
        )
        
        self.log("✓ Created test_calculator.py")
        self.log("✓ Test coverage: 100% of calculator methods")


def print_file_tree(vfs: VirtualFileSystem):
    """Print the VFS file tree."""
    print("\n" + "="*70)
    print("📁 PROJECT FILE TREE")
    print("="*70)
    
    files = vfs.list_files("/", recursive=True)
    
    for file_info in files.files:
        if file_info.file_type == FileType.DIRECTORY:
            icon = "📁"
        elif file_info.path.endswith(".py"):
            icon = "🐍"
        elif file_info.path.endswith(".md"):
            icon = "📝"
        else:
            icon = "📄"
        
        indent = "  " * (file_info.path.count("/") - 1)
        name = file_info.path.split("/")[-1] or "/"
        print(f"{indent}{icon} {name}")
    
    print("="*70)


def print_file_history(vfs: VirtualFileSystem, path: str):
    """Print the edit history of a file."""
    print(f"\n{'='*70}")
    print(f"📜 EDIT HISTORY: {path}")
    print(f"{'='*70}")
    
    history = vfs.get_file_history(path)
    
    for i, edit in enumerate(history, 1):
        print(f"\nEdit #{i}")
        print(f"  Agent: {edit.agent_id}")
        print(f"  Time: {edit.timestamp}")
        if edit.message:
            print(f"  Message: {edit.message}")
        print(f"  Content preview: {edit.content[:80]}...")
    
    print("="*70)


def main():
    """Run the multi-agent collaboration demo."""
    print("\n" + "="*70)
    print("MULTI-AGENT COLLABORATION DEMO")
    print("Using CaaS Virtual File System")
    print("="*70)
    
    # Create shared VFS
    vfs = VirtualFileSystem()
    print("\n✓ Shared Virtual File System initialized")
    
    # Initialize agents
    developer = DeveloperAgent(vfs)
    reviewer = ReviewerAgent(vfs)
    documenter = DocumenterAgent(vfs)
    tester = TesterAgent(vfs)
    
    print("\n" + "="*70)
    print("COLLABORATION WORKFLOW")
    print("="*70)
    
    # Step 1: Developer creates code
    print("\n[PHASE 1: Development]")
    developer.create_project_structure()
    
    # Step 2: Reviewer reviews and improves
    print("\n[PHASE 2: Code Review]")
    reviewer.review_code()
    
    # Step 3: Documenter adds documentation
    print("\n[PHASE 3: Documentation]")
    documenter.create_documentation()
    
    # Step 4: Tester creates tests
    print("\n[PHASE 4: Testing]")
    tester.create_tests()
    
    # Show final project structure
    print_file_tree(vfs)
    
    # Show edit history for calculator.py
    print_file_history(vfs, "/project/calculator.py")
    
    # Summary
    print("\n" + "="*70)
    print("COLLABORATION SUMMARY")
    print("="*70)
    
    state = vfs.get_state()
    file_count = len([f for f in state.files.values() if f.file_type == FileType.FILE])
    
    print(f"\n✓ Total files created: {file_count}")
    print(f"✓ Total agents involved: 4")
    print(f"✓ Total edits made: {sum(len(f.edit_history) for f in state.files.values())}")
    
    print("\nKEY BENEFITS:")
    print("  • All agents see each other's changes immediately")
    print("  • Complete edit history for auditability")
    print("  • Shared project state enables true collaboration")
    print("  • No file conflicts - agents work on shared VFS")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
