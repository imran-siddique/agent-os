"""Setup configuration for the Mute Agent package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mute-agent",
    version="0.1.0",
    author="Mute Agent Team",
    description="Decoupling Reasoning from Execution using Dynamic Semantic Handshake Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imran-siddique/mute-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies (none required for basic functionality)
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0,<9.0.0",
            "pytest-cov>=4.0.0,<6.0.0",
            "black>=22.0.0,<25.0.0",
            "flake8>=5.0.0,<8.0.0",
            "mypy>=0.990,<2.0.0",
        ],
    },
)
