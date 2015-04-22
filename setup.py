from setuptools import find_packages, setup


long_desc = '''\
Wallace is a wrapper for the Postgres, Redis, and Mongo database adapters.
It focuses on connection utilities and table-level abstractions but offers
a mini-ORM built around consistent attribute type declarations across
backends.
'''


if __name__ == '__main__':
    setup(
        packages=find_packages(),
        name='Wallace',
        version='0.0.8',
        author='Christopher Sira',
        author_email='cbsira@gmail.com',
        license='BSD',
        url='https://github.com/csira/wallace',
        description='Connection utilities, mini-ORM for PostgreSQL, Redis, and MongoDB.',
        long_description=long_desc,
        install_requires=[
            'psycopg2',
            'pymongo',
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
