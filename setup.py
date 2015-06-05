import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid==1.6a1',
    'transaction==1.4.4',
    'pyramid_tm==0.12',
    'pyramid_debugtoolbar==2.4',
    'zope.sqlalchemy==0.7.6',
    'SQLAlchemy==0.9.8',
    'psycopg2==2.5.4',
    'pyramid_jinja2==2.5',
    'WTForms==2.0.2',
    'paginate==0.4.3',
    'waitress==0.8.9',
    ]

setup(name='EmpProj',
      version='0.0',
      description='EmpProj',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='empproj',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = empproj:main
      [console_scripts]
      initialize_EmpProj_db = empproj.scripts.initializedb:main
      """,
      )
