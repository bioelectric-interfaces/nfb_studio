"""Install script for nfb_studio."""
from setuptools import setup, find_packages

install_requires = [
    "PySide2",
    "sortedcontainers",
    "xmltodict",
    "sympy",
    "pynfb @ https://github.com/bioelectric-interfaces/nfb/archive/0.1.1.zip",
]

extras_require = {
    "docs": [
        "sphinx",
        "sphinx-rtd-theme"
    ],
    "freeze": [
        "pyinstaller",
    ]
}

entry_points = {
    "gui_scripts": ["nfb-studio = nfb_studio.__main__:main"],
    "console_scripts": ["nfb-studio-d = nfb_studio.__main__:main"],
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
    extras_require=extras_require,
    entry_points=entry_points
)
