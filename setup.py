from setuptools import (
    find_packages,
    setup,
)

install_requires = [
    'setuptools',
]

tests_require = [
    'coverage',
    'pytest',
]

dependency_links = [
]

setup(
    name='dotted-name-resolver',
    version='1.0',
    description='Dotted name resolver (stollen from pyramid.path)',
    author='',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='dotted_name_resolver.tests',
    extras_require={
        'test': tests_require,
    },
    dependency_links=dependency_links,
    entry_points={
    }
)
