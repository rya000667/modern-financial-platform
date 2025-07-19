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
        "scripts/fidelity_wpx_cash_dividends.py",
        "scripts/interactive_brokers_account_summary.py",
        "scripts/interactive_brokers_flex_statements.py"
    ],
    install_requires=[
        "requests",
        "pandas",
        "lxml",
        "ibflex",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
