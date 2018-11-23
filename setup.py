try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
from setuptools import setup, find_packages

CURRENT_VERSION = "v2.1.0"

setup(
    name='casper',
    description='Casper is a command line tool that interacts with Cloud Deploy (Ghost project).',
    version=CURRENT_VERSION,
    python_requires='>=3.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[str(ir.req) for ir in parse_requirements('requirements.txt', session='hack')],
    # https://github.com/pypa/pip/issues/4187.
    dependency_links=[str(ir.link) + '-0' for ir in parse_requirements('requirements.txt', session='hack') if ir.link],
    entry_points={
        'console_scripts': [
            'casper=casper.main:cli',
        ],
    },
)
