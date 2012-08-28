#!/usr/bin/env python
# -*- coding=utf-8 -*-

from distutils.core import setup
import siderus

setup(name='siderus',
      version=siderus.__version__,
      description='Siderus Peer-To-Peer Network',
      author='Lorenzo Setale',
      author_email='koalalorenzo@gmail.com',
      license=siderus.__license__,
      url='http://sider.us/',
      packages=['siderus'],
     )