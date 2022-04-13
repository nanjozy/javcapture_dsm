# -*- coding: utf-8 -*-
import os

from pylibz import get_now, Path
from setuptools import find_packages, setup

root_path = Path(__file__).resolve().absolute().parent.as_posix()
os.chdir(root_path)

# python setup.py bdist_wheel

long_description = ""
extras_require = {
}
requires = [
]
setup(
    name="javcapture",
    version=str(get_now()),
    packages=find_packages(
    ),
    platforms="any",
    author="",
    author_email="",
    description="common package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="PSF",
    keywords="common package",
    extras_require=extras_require,
    install_requires=requires,
    url="",
    include_package_data=True,
    zip_safe=True,
    package_data={
    },
    entry_points={
    }
)
