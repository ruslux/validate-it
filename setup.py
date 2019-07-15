from os import path

from setuptools import setup, find_packages

version = "0.9.3"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="validate-it",
    packages=find_packages(exclude=('benchmarks', 'tests')),
    version=version,
    description="Schema validator built on top of the typing module",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Ruslan Roskoshnyj",
    author_email="i.am.yarger@gmail.com",
    url="https://github.com/ruslux/validate_it",
    download_url="https://github.com/ruslux/validate_it/archive/{}.tar.gz".format(version),
    keywords=["schema", "validator", "json", "typing", "annotations"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires=">=3.6.0,>=3.7.0",
    platforms=["OS Independent"],
    license="LICENSE.txt",
    install_requires=[],
    extras_require={
        "tests": [
            "pytest (==3.4.0)",
            "coverage (==4.5)",
            "pytest-cov (==2.5.1)",
        ]
    }
)
