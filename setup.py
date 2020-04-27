# -*- coding: utf-8 -*-
#
# Copyright 2016 Tickaroo GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from setuptools import setup, find_packages

version = '0.0.14'

setup(name='livebridge-tickaroo',
      version=version,
      description="Livebridge adapter for Tickaroo.",
      long_description="""\
Allows to use Tickaroo tickers as target for Livebridge.\
See https://github.com/tickaroo/livebridge-tickaroo for more infos.
""",
      classifiers=[
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications :: Chat", 
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Other Audience",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Environment :: Plugins",
        ],
      keywords=['liveticker','tickaroo','syndication'],
      author='Tickaroo GmbH',
      maintainer='Andreas Gerauer',
      maintainer_email='andi@tickaroo.com',
      url='https://github.com/tickaroo/livebridge-tickaroo',
      license='Apache Software License (http://www.apache.org/licenses/LICENSE-2.0)',
      packages = find_packages(exclude=['tests', 'htmlcov']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "livebridge>=0.10.0",
        "beautifulsoup4"
      ])

