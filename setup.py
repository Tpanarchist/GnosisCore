from setuptools import setup, find_packages

setup(
    name="gnosiscore",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.24.0",
        "networkx>=3.0",
        "PyJWT>=2.6.0",
        "pynacl>=1.5.0",
        "websockets>=11.0",
    ],
    python_requires=">=3.11",
)
