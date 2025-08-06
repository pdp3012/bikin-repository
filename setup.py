#!/usr/bin/env python3
"""
Setup script untuk Tokopedia Scraper
Dibuat oleh: Dosen Data Mining dengan 30 tahun pengalaman
"""

from setuptools import setup, find_packages
import os

# Baca README.md
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Baca requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tokopedia-scraper",
    version="1.0.0",
    author="Dosen Data Mining",
    author_email="dosen.datamining@example.com",
    description="Scraper Tokopedia yang canggih dengan fitur scrolling otomatis dan analisis data",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/dosen-datamining/tokopedia-scraper",
    packages=find_packages(),
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
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tokopedia-scraper=tokopedia_scraper:main",
            "tokopedia-analyzer=data_analyzer:main",
            "tokopedia-test=test_scraper:main",
            "tokopedia-example=example_usage:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json"],
    },
    keywords=[
        "scraping",
        "tokopedia",
        "e-commerce",
        "data-mining",
        "selenium",
        "beautifulsoup",
        "pandas",
        "analysis",
        "visualization",
    ],
    project_urls={
        "Bug Reports": "https://github.com/dosen-datamining/tokopedia-scraper/issues",
        "Source": "https://github.com/dosen-datamining/tokopedia-scraper",
        "Documentation": "https://github.com/dosen-datamining/tokopedia-scraper#readme",
    },
)