"""
Mambo
An elegant static site generator
"""

import os
from setuptools import setup, find_packages


base_dir = os.path.dirname(__file__)

__about__ = {}

with open(os.path.join(base_dir, "mambo", "__about__.py")) as f:
    exec(f.read(), __about__)

install_requires = [
    "jinja2==2.10.1",
    "click==6.2",
    "pyyaml==4.2b1",
    "markdown==2.6.2",
    "python-frontmatter==0.4.5",
    "htmlmin==0.1.5",
    "livereload==2.5.0",
    "arrow==0.8.0", 
    "python-slugify==1.2.1",
    "pyScss"
]

setup(
    name="mambo",
    version=__about__["__version__"],
    license=__about__["__license__"],
    author=__about__["__author__"],
    author_email=__about__["__email__"],
    description=__about__["__summary__"],
    url=__about__["__uri__"],
    long_description=__about__["__long_description__"],
    py_modules=['mambo'],
    entry_points=dict(console_scripts=[
        'mambo=mambo.cli:cmd'
    ]),
    include_package_data=True,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    keywords=['static site generator'],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)