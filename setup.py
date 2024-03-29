from setuptools import setup, find_packages

__version__ = 'undefined'

with open('ming/version.py') as r:
	data = r.read()
	exec(data)

setup(name='Ming',
      version=__version__,
      description="Bringing order to Mongo since 2009",
      long_description="""Database mapping layer for MongoDB on Python. Includes schema enforcement and some facilities for schema migration. 
""",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='mongo, pymongo',
      author='Rick Copeland',
      author_email='rick@geek.net',
      url='http://merciless.sourceforge.net',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
        "mock >=0.6.0,<0.7.99",
        "FormEncode >= 1.2.1",
        "pymongo>=2.0",
        "PasteScript", # used by flyway
        "WebOb",
        # "python-spidermonkey >= 0.0.10", # required for full MIM functionality
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_factory]
      ming_autoflush=ming.orm.middleware:make_ming_autoflush_middleware

      [flyway.test_migrations]
      a = flyway.tests.migrations_a
      b = flyway.tests.migrations_b

      [paste.paster_command]
      flyway = flyway.command:MigrateCommand
      """,
      test_suite='nose.collector'
      )
