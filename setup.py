from setuptools import setup

setup(name='sdb_grid_reader',
    version='0.0.1',
    description='Tool for accessing a processed grid of MESA sdB models.',
    url='https://github.com/cespenar/sdb_grid_processor',
    author='Jakub Ostrowski',
    author_email='cespenar1@gmail.com',
    license='MIT',
    packages=['sdb_grid_processor'],
    install_requires=['mesa_reader', 'sqlalchemy'])
