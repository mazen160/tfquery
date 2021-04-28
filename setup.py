from setuptools import setup


setup(name='tfquery',
      version='0.0.1',
      author='Mazin Ahmed',
      author_email='mazin@mazinahmed.net',
      packages=['tfquery'],
      entry_points={'console_scripts': ['tfquery=tfquery.__main__:main']},
      url='http://pypi.python.org/pypi/tfquery/',
      license='LICENSE.md',
      description='tfquery: Run SQL queries on your Terraform infrastructure. Query resources and analyze its configuration using a SQL-powered framework.',
      long_description=open('README.md').read())
