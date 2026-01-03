from setuptools import setup, find_packages

setup(
    name="context-as-a-service",
    version="0.1.0",
    description="A managed pipeline for intelligent context extraction and serving",
    author="Context-as-a-Service Team",
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
)
