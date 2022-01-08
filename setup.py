#!/usr/bin/env python

from setuptools import setup, find_packages


requirements = []

setup(
    author="Camille Scott",
    author_email='cswel@ucdavis.edu',
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'dashboard = dashboard.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    name='dashboard',
    packages=find_packages(include=['dashboard', 'dashboard.*']),
    test_suite='tests',
    version='0.1',
    zip_safe=False,
)
