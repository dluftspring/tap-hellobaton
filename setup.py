from setuptools import setup, find_packages

setup(
    name='tap-hellobaton',
    version='0.0.3',
    description='Singer.io tap for extracting data from the Hello Baton API',
    author='Daniel Luftspring',
    py_modules=['tap_hellobaton'],
    install_requires=[
        'singer-sdk>=0.3.17',
        'requests>=2.26.0',
        'urllib3>=1.26.7',
        'jsonschema>=3.2.0'
    ],
    entry_points='''
        [console_scripts]
        tap-hellobaton=tap_hellobaton.tap:Taphellobaton.cli
    ''',
    packages=['tap_hellobaton'],
    package_data = {
        'tap_hellobaton': [
            'schemas/*.json'
        ]
    },
    include_package_data=True
)