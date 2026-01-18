from setuptools import setup, find_packages

setup(
    name="self-correcting-agent-kernel",
    version="0.1.0",
    description="Self-correcting agent kernel that analyzes failures and patches agents",
    author="Self-Correcting Agent Team",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "streamlit>=1.28.0",
            "jupyter>=1.0.0",
        ],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "streamlit>=1.28.0",
            "jupyter>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "scak=cli:main",
        ],
    },
    python_requires=">=3.8",
)
