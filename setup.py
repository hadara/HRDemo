import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid==1.4.5',
    'transaction==1.4.1',
    'pyramid_tm==0.7',
    'pyramid_debugtoolbar==1.0.9',
    'zope.sqlalchemy==0.7.3',
    'SQLAlchemy==0.8.3',
    'psycopg2==2.5.1',
    'pyramid_jinja2==1.9',
    'WTForms==1.0.5',
    'paginate==0.4.1',
    'waitress==0.8.7',
    'uWSGI==2.0'
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
