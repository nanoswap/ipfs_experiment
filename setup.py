# from __future__ import annotations

from typing import List
from setuptools import setup, find_packages

def load_long_description(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

setup(
    name="ipfs_experiment",
    version="0.0.1",
    author="Nathaniel Schultz",
    author_email="nate@nanoswap.finance",
    description="IPFS Experiment",
    long_description=load_long_description("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/nanoswap/ipfs_experiment/issues",
    project_urls={
        "Bug Tracker": "https://github.com/mahesh-maximus/helloworld-pyp/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: The Unlicense (Unlicense)"

    ],
    package_dir={'':"src"},
    packages=find_packages("src"),
    python_requires=">=3.6"
)
