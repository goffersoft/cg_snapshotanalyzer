from setuptools import setup

setup(
    name='snapshotanalyzer',
    version='0.1',
    author='goffer',
    author_email="goffersoft@gmail.com",
    description='tools to manage EC2 snapshots',
    license="GPLv3+",
    packages=['analyzer'],
    url="https://github.com/goffersoft/cg_snapshotanalyzer",
    install_requires=[
          'click',
          'boto3'
    ],
    entry_points='''
          [console_scripts]
          snapshotanalyzer=analyzer.snapshotanalyzer:cli 
    ''',
)
