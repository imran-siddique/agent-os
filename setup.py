from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scak",  # Short, memorable PyPI name
    version="1.1.0",
    description="Self-Correcting Agent Kernel: Automated alignment via differential auditing and semantic memory hygiene for production AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Self-Correcting Agent Team",
    author_email="research@scak.ai",
    url="https://github.com/imran-siddique/self-correcting-agent-kernel",
    project_urls={
        "Bug Tracker": "https://github.com/imran-siddique/self-correcting-agent-kernel/issues",
        "Documentation": "https://github.com/imran-siddique/self-correcting-agent-kernel/wiki",
        "Source Code": "https://github.com/imran-siddique/self-correcting-agent-kernel",
        "Changelog": "https://github.com/imran-siddique/self-correcting-agent-kernel/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests*", "experiments*", "examples*", "notebooks*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
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
    keywords="ai agents self-correction alignment differential-auditing semantic-purge llm production-ml scak self-correcting-kernel",
    license="MIT",
)
