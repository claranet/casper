from setuptools import setup, find_packages

setup(
    name='casper',
    version='2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        casper=casper.main:cli
    ''',
)
