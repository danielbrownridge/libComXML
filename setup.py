# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='libComXML',
    version='0.0.4',
    url='http://git.gisce.lan/libComXML.git',
    author='GISCE Enginyeria, SL',
    author_email='devel@gisce.net',
    packages=['libcomxml', 'libcomxml.core', 'libcomxml.messages'],
    requires=['lxml'],
    license='None',
    description='libComXML',
    long_description=open('README').read(),
)
