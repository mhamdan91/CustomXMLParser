import os
from setuptools import setup, find_packages
from pip._internal.network.session import PipSession
from pip._internal.req.req_file import parse_requirements
from CustomXMLParser.version import __version__
VERSION = __version__
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
REQUIREMENTS = parse_requirements(os.path.join(PROJECT_DIR, 'requirements.txt'), session=PipSession())
DESCRIPTION = 'Python Libary that allows for customized parsing of XML files using a set of configurations. '  \
              'Output is a dictonary. This library builds on the xml2dict library.'
LONG_DESCRIPTION = open('README.md').read()
setup(
    name="CustomXMLParser",
    version=VERSION,
    author="mhamdan91 (Hamdan, Muhammad)",
    author_email="<mhamdan.dev@gmail.com>",
    url='https://github.com/mhamdan91/CustomXMLParser',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[str(ir.requirement) for ir in REQUIREMENTS],
    keywords=['python', 'xml', 'XML', 'parsing', 'mapping', 'dictionary', 'configurable', 'custom', 'formatting'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: BSD License",
    ]
)