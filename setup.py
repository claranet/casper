from pip.req import parse_requirements
from setuptools import setup, find_packages

requirements = parse_requirements('requirements.txt', session='hack')

setup(
    name='casper',
    version='2.0',
    python_requires='>=3.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[str(ir.req) for ir in requirements],
    entry_points='''
        [console_scripts]
        casper=casper.main:cli
    ''',
)
