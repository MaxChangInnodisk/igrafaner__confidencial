from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setup(
    name='igrafaner',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='The helper model for siamese model.',
    author='Max',
    author_email='max_chang@innodisk.com',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'igra-cli = igrafaner.main:cli'
        ]
    }
)