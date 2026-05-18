from setuptools import setup, find_packages

setup(
    name="vestara-app",
    version="1.0.0",
    packages=find_packages(where="vestara"),
    package_dir={"": "vestara"},
    python_requires=">=3.10",
)
