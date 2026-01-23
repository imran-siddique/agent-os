from setuptools import setup, find_packages

setup(
    name="iatp",
    version="0.1.0",
    description="Inter-Agent Trust Protocol - Zero-Config Sidecar for Agent Communication",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.1",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.3",
        "httpx>=0.26.0",
        "python-dateutil>=2.8.2",
    ],
    python_requires=">=3.8",
)
