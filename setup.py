from setuptools import setup, find_packages

__author__ = 'Naor Livne'
__author_email__ = 'naorlivne@gmail.com'
__version__ = '0.1.4'

# read the README.md file for the long description of the package
with open('README.md') as f:
    long_description = f.read()

# minimum requirement list
requirements = [
    "PyYAML",
    "toml",
    "configobj"
]

setup(name='parse_it',
      author=__author__,
      author_email=__author_email__,
      version=__version__,
      description="A python library for parsing multiple types of config files, envvars and command line arguments "
                  "which takes the headache out of setting app configurations.",
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      scripts=['setup.py'],
      license="GPLv3",
      keywords="parse_it parsing parse config configuration",
      url="https://github.com/naorlivne/parse_it",
      install_requires=requirements,
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Environment :: Other Environment",
                   "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Operating System :: OS Independent",
                   "Intended Audience :: Developers",
                   "Intended Audience :: System Administrators",
                   "Topic :: Software Development :: Libraries :: Python Modules"])
