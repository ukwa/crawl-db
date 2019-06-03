import subprocess
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

def get_version():
    try:
        return subprocess.check_output(['git', 'describe', '--tags', '--always']).strip().decode("utf-8")
    except:
        return "?.?.?"

setup(
    name='crawldb',
    version=get_version(),
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    license='Apache 2.0',
    long_description=open('README.md').read(),
    zip_safe = False, # Avoid installing as .egg file, as Luigi can't handle these.
    entry_points={
        'console_scripts': [
            'crawldb=crawldb.cli:main'
        ]
    }
)
