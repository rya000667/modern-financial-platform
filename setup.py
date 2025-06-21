from setuptools import setup, find_packages

setup(
    name="financial_investing_platform",
    version="0.1.0",
    description="A platform for financial investing analysis, including Black-Scholes option pricing.",
    author="Ryan Harrington",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    scripts=[
        "scripts/blackScholes.py",
        "scripts/fidelity_wpx_cash_dividends.py"
    ],
    install_requires=[],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
