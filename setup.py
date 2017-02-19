#! /usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import sys
    reload(sys).setdefaultencoding("UTF-8")
except:
    pass

try:
    from setuptools import setup, find_packages
except ImportError:
    print 'Please install or upgrade setuptools or pip to continue.'
    sys.exit(1)


TEST_REQUIRES = []

INSTALL_REQUIRES = ['numpy',
                    'pandas',
                    'statsmodels',
                    ] + TEST_REQUIRES

setup(name='dominion-analysis',
      description='Analysis of Dominion game ratings',
      version='0.01',
      author='Matt Peddie',
      author_email='mpeddie@gmail.com',
      maintainer='Matt peddie',
      maintainer_email='mpeddie@gmail.com',
      url='https://github.com/peddie/dominion-analysis',
      keywords='',
      classifiers=['Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: MacOS :: MacOS X',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Programming Language :: Python :: 2.7'
                   ],
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES,
      tests_require=TEST_REQUIRES,
      setup_requires=[],
      platforms="Linux,Windows,Mac",
      use_2to3=False,
      zip_safe=False)
