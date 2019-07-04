from setuptools import setup, find_packages


__author__ = 'Naor Livne'
__author_email__ = 'naorlivne@gmail.com'
__version__ = "0.9.1"

# read the README.md file for the long description of the package
with open('README.md') as f:
    long_description = f.read()

# minimum requirement list
requirements = [
    "PyYAML",
    "toml",
    "configobj",
    "xmltodict",
    "pyhcl"
]

# optional requirements, typing is used for support of Python versions 3.4 & lower, note 3.4 and lower is untested
extra_requirements = {
          'typing':  ["typing"]
      }

setup(
    name='parse_it',
    author=__author__,
    author_email=__author_email__,
    version=__version__,
    description="A python library for parsing multiple types of config files, envvars and command line arguments "
                "which takes the headache out of setting app configurations.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    extras_require=extra_requirements,
    scripts=['setup.py'],
    license="LGPLv3",
    keywords="parse_it parsing parse parser yaml json xml toml ini cfg hcl envvar environment_variable config "
             "cli_args command_line_arguments tml yml configuration configuration_file",
    url="https://github.com/naorlivne/parse_it",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
        ]
)
