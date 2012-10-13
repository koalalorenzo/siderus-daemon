#!/usr/bin/env python
# -*- coding=utf-8 -*-

from distutils.core import setup
import re

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements

setup(name='siderus',
      version="0.4",
      description='Siderus Peer-To-Peer Network',
      author='Lorenzo Setale',
      author_email='koalalorenzo@gmail.com',
      license="See: http://creativecommons.org/licenses/by-nd/3.0/ ",
      url='http://sider.us/',
      packages=['siderus'],
      install_requires = parse_requirements('requirements.txt'),
     )