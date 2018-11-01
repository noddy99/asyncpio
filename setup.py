import os
import re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


long_description = read('README.md')

setup(name='asyncpio',
      version=find_version('asyncpio.py'),
      author='Sam Thomson',
      maintainer='Sam Thomson',
      url='https://github.com/spthm/asyncpio',
      description='Python module for asynchronous access to the pigpio daemon',
      long_description=long_description,
      long_description_content_type='text/markdown',
      download_url='https://github.com/spthm/asyncpio/archive/master.zip',
      license='unlicense.org',
      py_modules=['asyncpio'],
      keywords=['raspberrypi', 'gpio',],
      classifiers=[
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3.5",
         "Programming Language :: Python :: 3.6",
         "Programming Language :: Python :: 3.7",
      ],
      python_requires=">=3.5"
     )

