from setuptools import setup

setup(
    name='curami',
    version='2.0.0',
    packages=['curami', 'curami.commons', 'curami.collection', 'curami.preprocess', 'curami.analysis'],
    package_dir={'': './'},
    url='https://github.com/EBIBioSamples/curami-v2',
    license='Apache License 2.0',
    author='isuru',
    author_email='isuru@ebi.ac.uk',
    description='Curating EBI BioSamples '
)
