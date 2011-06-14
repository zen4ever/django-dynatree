#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='django-dynatree',
      version='1.0',
      description='Django forms widget that uses Dynatree to display tree data',
      author='Andrii Kurinnyi',
      author_email='andrew@zen4ever.com',
      url='https://github.com/zen4ever/django-dynatree',
      packages=['dynatree',],
      keywords=['django', 'dynatree', 'mptt', 'tree'],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Framework :: Django',
      ],
      long_description=open(
          os.path.join(os.path.dirname(__file__), 'README.rst'),
      ).read().strip(),
)
