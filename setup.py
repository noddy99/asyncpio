#!/usr/bin/env python3

from distutils.core import setup

setup(name='copigpio',
      version='0.0.1',
      author='Sam Thomson',
      maintainer='Sam Thomson',
      url='https://github.com/spthm/copigpio',
      description='Raspberry Pi GPIO module',
      long_description='Python module for asynchronous access to the pigpio daemon',
      download_url='https://github.com/spthm/copigpio/archive/master.zip',
      license='unlicense.org',
      py_modules=['copigpio'],
      keywords=['raspberrypi', 'gpio',],
      classifiers=[
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3.5",
         "Programming Language :: Python :: 3.6",
         "Programming Language :: Python :: 3.7",
      ],
      python_requires=">=3.5"
     )

