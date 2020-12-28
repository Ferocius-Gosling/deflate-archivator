from setuptools import setup, find_packages

setup(name='deflate-archivator',
      version='1.0',
      url='https://github.com/Ferocius-Gosling/deflate-archivator',
      description='Deflate compressor',
      packages=find_packages(),
      test_suite='tests',
      install_requires=['bitarray', 'pytest'],
      entry_points={
          'console_scripts': ['deflate=deflate.__main__']
      }
      )
