from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read the contents of requirements file
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="ai-collaborative-writing",
    version="0.1.0",
    author="AI Collaborative Writing Team",
    author_email="team@collaborativewriter.com",
    description="An AI collaborative novel writing system with multiple specialized agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/writeAgent",
    project_urls={
        "Bug Reports": "https://github.com/your-username/writeAgent/issues",
        "Source": "https://github.com/your-username/writeAgent",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(where="src", include=["src*"]),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "collaborative-writer=src.main:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
        "deploy": [
            "docker",
            "gunicorn",
        ],
    },
    keywords="ai, writing, collaboration, novel, agents, langgraph, llm",
    include_package_data=True,
    zip_safe=False,
)