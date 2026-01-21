from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="context-as-a-service",
    version="0.1.0",
    description="A managed pipeline for intelligent context extraction and serving",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Context-as-a-Service Team",
    url="https://github.com/imran-siddique/context-as-a-service",
    project_urls={
        "Bug Reports": "https://github.com/imran-siddique/context-as-a-service/issues",
        "Source": "https://github.com/imran-siddique/context-as-a-service",
        "Documentation": "https://github.com/imran-siddique/context-as-a-service/tree/main/docs",
    },
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "PyPDF2>=3.0.1",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
        "python-multipart>=0.0.6",
        "tiktoken>=0.5.1",
        "numpy>=1.26.2",
        "scikit-learn>=1.3.2",
        "aiofiles>=23.2.1",
    ],
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="context rag document-processing ai nlp context-extraction enterprise trust-gateway",
    entry_points={
        "console_scripts": [
            "caas=caas.cli:main",
        ],
    },
)
