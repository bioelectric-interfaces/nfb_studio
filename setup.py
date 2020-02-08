from setuptools import setup
from importlib.util import find_spec

install_requires = [
    "PySide2",
    "sortedcontainers"
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
        "nfb_studio": ["*.svg"]
    },
    extras_require=extras_require
)
