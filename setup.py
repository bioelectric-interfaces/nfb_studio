"""Install script for nfb_studio."""
from setuptools import setup, find_packages

install_requires = [
    "PySide2",
    "sortedcontainers",
    "xmltodict",
    "pynfb @ https://github.com/andreasxp/nfb/archive/a4e7273d07c6d8d55b4f6a9bb366a883f3db6b54.zip",
]

extras_require = {
    "docs": ["pdoc3"],
    "freeze": [
        "pyinstaller",
    ]
}

setup(
    name="nfb_studio",
    version="0.1",
    description="Design application for NFB experiments",
    author="Andrey Zhukov",
    author_email="andres.zhukov@gmail.com",
    license="MIT",
    install_requires=install_requires,
    packages=find_packages(),
    package_data={
        "nfb_studio": ["assets/*"]
    },
    extras_require=extras_require
)
