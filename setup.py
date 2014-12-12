from setuptools import find_packages, setup


long_desc = '''\
Wallace is a wrapper for the Postgres and Redis database adapters (more to
come) that provides a small ORM and other db connection utilities.
'''


if __name__ == '__main__':
    setup(
        packages=find_packages(),
        name='Wallace',
        version='0.0.2',
        author='Christopher Sira',
        author_email='cbsira@gmail.com',
        license='BSD',
        url='https://github.com/csira/wallace',
        description='ORM and connection utilities for PostgreSQL and Redis.',
        long_description=long_desc,
        install_requires=[
            'psycopg2',
            'redis',
            'ujson',
        ],
        classifiers=[
            'Development Status :: 3 - Alpha',
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
