try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
from setuptools import setup, find_packages

CURRENT_VERSION = "v2.2.1"

setup(
    name='casper',
    description='Casper is a command line tool that interacts with Cloud Deploy (Ghost project).',
    version=CURRENT_VERSION,
    python_requires='>=3.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=["{} @ {}".format(ir.req, ir.link) if ir.link else str(ir.req)
                      for ir in parse_requirements('requirements.txt', session='hack')],
    entry_points={
        'console_scripts': [
            'casper=casper.main:cli',
        ],
    },
)
