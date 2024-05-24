from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as fh:
    long_description = '\n' + fh.read()

VERSION = '0.0.1.1'
DESCRIPTION = 'Enumerating networks and finding optimal pathways'

# Setting up
setup(
    name='kers',
    version=VERSION,
    author='a-ware (Project A-ware)',
    author_email='<all@stickybits.red>',
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests', 'python3-nmap', 'paramiko', 'bs4', 'scp'],
    keywords=['python', 'enumeration', 'reconnaissance', 'c2', 'breach-simulation', 'network-analysis'],
    classifiers=[
        'Development Status :: 2 - Development',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ]
)