from setuptools import setup

name = 'motile'
here = os.path.abspath(os.path.dirname(__file__))
version_info = {}
with open(os.path.join(here, name, 'version_info.py')) as fp:
    exec(fp.read(), version_info)
version = version_info['_version']

setup(
        name=name,
        version=str(version),
        description='Multi-Object Tracker using Integer Linear Equations',
        url='https://github.com/funkelab/motile',
        author='Jan Funke',
        author_email='funkej@janelia.hhmi.org',
        license='MIT',
        packages=[
            'motile',
            'motile.constraints',
            'motile.costs',
            'motile.variables'
        ],
        install_requires=[
            'networkx',
            'ilpy @ git+https://github.com/funkelab/ilpy',
            'numpy'
        ]
)
