from setuptools import setup
from importlib.util import find_spec

install_requires = [
    "Qt.py",
    "sortedcontainers"
]

# Check if a Qt implementation needs to be installed
if find_spec("PyQt5") is None and find_spec("PySide2") is None:
    install_requires.append("PySide2")

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
    }
)
