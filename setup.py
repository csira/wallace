from setuptools import find_packages, setup


# python setup.py sdist
# python setup.py sdist upload


long_desc = '''\
Wallace is an API for modeling data with the Postgres (psycopg2), Redis (redis-py)
and Mongo (pymongo) database adaptors.
'''

packages = [pkg for pkg in find_packages() if pkg.startswith('wallace')]

if __name__ == '__main__':
    setup(
        # packages=find_packages(),
        packages=packages,
        name='Wallace',
        version='0.9.1',
        author='Christopher Sira',
        author_email='cbsira@gmail.com',
        license='BSD',
        url='https://github.com/csira/wallace',
        description='An API for modeling data with psycopg2, redis-py, and pymongo.',
        long_description=long_desc,
        install_requires=[
            'psycopg2',
            'pymongo',
            'redis',
            'ujson',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: Freely Distributable',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Topic :: Database',
            'Topic :: Database :: Database Engines/Servers',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
