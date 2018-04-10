from pip.req import parse_requirements
from setuptools import setup, find_packages
from casper.main import CURRENT_VERSION

requirements = parse_requirements('requirements.txt', session='hack')

setup(
    name='casper',
    version=CURRENT_VERSION,
    python_requires='>=3.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[str(ir.req) for ir in requirements],
    entry_points='''
        [console_scripts]
        casper=casper.main:cli
    ''',
)
