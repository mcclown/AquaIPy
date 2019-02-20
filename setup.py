from __future__ import print_function
from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import aquaipy

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


# Convert README.md with pandoc
long_description = read('README.rst')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["-rxXs"]
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)
        

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

setup(
    name='aquaipy',
    version=aquaipy._VERSION_,
    url='http://github.com/mcclown/AquaIPy/',
    license='Apache Software License',
    author='Stephen Mc Gowan',
    tests_require=['pytest'],
    install_requires=['requests>=2.18.4'],
    cmdclass={'test': PyTest, 'clean': CleanCommand},
    author_email='mcclown@gmail.com',
    description='Python library for controlling the AquaIllumination range of aquarium lights',
    long_description=long_description,
    packages=['aquaipy'],
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)

