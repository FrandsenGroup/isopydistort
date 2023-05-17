#!/usr/bin/env python
##############################################################################
#
# isopydistort         by Frandsen Group
#                     Benjamin A. Frandsen benfrandsen@byu.edu
#                     (c) 2023 Benjamin Allen Frandsen
#                      All rights reserved
#
# File coded by:    Benjamin Frandsen
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

# Installation script for isopydistort

"""isopydistort - Tools for interfacing with the ISODISTORT web server.
Packages:   isopydistort
"""

import os
from setuptools import setup, find_packages

# define distribution
setup_args = dict(
        name = "isopydistort",
        version = '0.1',
        namespace_packages = [],
        packages = find_packages(),
        test_suite = 'isopydistort.tests',
        include_package_data = True,
        zip_safe = False,
        author = 'Benjamin A. Frandsen group',
        author_email = 'benfrandsen@byu.edu',
        maintainer = 'Benjamin Frandsen',
        maintainer_email = 'benfrandsen@byu.edu',
        description = "Tools for interfacing with ISODISTORT.",
        license = 'BSD-3-clause',
        url = "https://github.com/FrandsenGroup/isopydistort",
        keywords = "",
        classifiers = [
            # List of possible values at
            # http://pypi.python.org/pypi?:action=list_classifiers
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Programming Language :: Python :: 3.7',
            'Topic :: Scientific/Engineering :: Physics',
        ],
)

if __name__ == '__main__':
    setup(**setup_args)

# End of file
