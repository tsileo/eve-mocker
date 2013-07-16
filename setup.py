import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="eve-mocker",
    version="0.1.0",
    author="Thomas Sileo",
    author_email="thomas.sileo@gmail.com",
    description="Mocking tool for Eve powered REST API.",
    license="MIT",
    keywords="eve api mock mocking mocker",
    url="https://github.com/tsileo/eve-mocker",
    py_modules=["eve_mocker"],
    long_description=read("README.rst"),
    install_requires=["httpretty"],
    tests_require=["sure", "requests"],
    test_suite="test_eve_mocker",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)
