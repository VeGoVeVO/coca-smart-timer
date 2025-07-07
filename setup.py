#!/usr/bin/env python3
"""
Setup script for COCA Smart Timer
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("coca-timer/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="coca-smart-timer",
    version="1.0.0",
    author="COCA Timer Team",
    description="A smart overlay timer for gaming with OCR percentage detection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/coca-smart-timer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "coca-timer=coca_timer.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "coca_timer": ["assets/*"],
    },
)
