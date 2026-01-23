#!/usr/bin/env python
"""
Setup script for Agent Control Plane
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="agent-control-plane",
    version="1.2.0",
    author="Agent Control Plane Contributors",
    author_email="",
    description="A governance and management layer for autonomous AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imran-siddique/agent-control-plane",
    project_urls={
        "Bug Tracker": "https://github.com/imran-siddique/agent-control-plane/issues",
        "Documentation": "https://github.com/imran-siddique/agent-control-plane/tree/main/docs",
        "Source Code": "https://github.com/imran-siddique/agent-control-plane",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="ai agents governance control-plane safety policy",
    zip_safe=False,
)
