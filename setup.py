"""
Setup script for jmap-engine
"""

from setuptools import setup, find_packages
import os

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read version
version = {}
with open('jmap_engine/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)

setup(
    name='jmap-engine',
    version=version['__version__'],
    author='cocdeshijie',
    author_email='',
    description='Python library for viewing and sending emails through the JMAP protocol',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cocdeshijie/jmap-engine',
    project_urls={
        'Bug Tracker': 'https://github.com/cocdeshijie/jmap-engine/issues',
        'Documentation': 'https://github.com/cocdeshijie/jmap-engine#readme',
        'Source Code': 'https://github.com/cocdeshijie/jmap-engine',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'docs']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.25.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
            'mypy>=0.910',
        ],
    },
    keywords='jmap email rfc8620 rfc8621 mail protocol',
    include_package_data=True,
    zip_safe=False,
)
