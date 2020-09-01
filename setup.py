"""Install script for nfb_studio."""
from setuptools import setup

install_requires = [
    "PySide2",
    "sortedcontainers",
    "xmltodict",
    "pynfb @ https://github.com/andreasxp/nfb/archive/c2854cc530a634bd446984ab55c7802e84faaf59.zip",
]

extras_require = {
    "docs":  ["pdoc3"]
}

setup(
    name="nfb_studio",
    version="0.1",
    description="Design application for NFB experiments",
    author="Andrey Zhukov",
    author_email="andres.zhukov@gmail.com",
    license="MIT",
    install_requires=install_requires,
    package_data={
        "nfb_studio": ["assets/*"]
    },
    extras_require=extras_require
)
