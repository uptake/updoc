import io

from setuptools import find_packages
from setuptools import setup

VERSION = {}
with open("./docserver/__version__.py") as fp:
    exec(fp.read(), VERSION)

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='docserver',
    version=VERSION['__version__'],
    url='http://github.com/uptake/updoc',
    license='BSD 3-Clause',
    maintainer='Hao-En Tsui',
    maintainer_email='opensource@uptake.com',
    description='An application for serving documentation in a cloud environment.',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'boto3',
        'botocore',
        'flask',
        'gunicorn',
        'redis',
        'sphinx',
        'sphinxcontrib-napoleon',
        'sphinx-rtd-theme',
        'sphinxcontrib-programoutput',
        'sphinxcontrib-websupport',
        'pillow'
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
            'requests'
        ]
    }
)
