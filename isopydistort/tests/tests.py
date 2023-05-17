#!/usr/bin/env python
##############################################################################
#
# diffpy.mpdf         by Frandsen Group
#                     Benjamin A. Frandsen benfrandsen@byu.edu
#                     (c) 2022 Benjamin Allen Frandsen
#                      All rights reserved
#
# File coded by:    Benjamin Frandsen
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Unit tests basic pydistort functionalities. Execute via
python -m pydistort.tests.tests
"""

import unittest
import pydistort
import sys
import os

##############################################################################
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

class testBasic(unittest.TestCase):
    def test_get(self):
        print('Testing connection to ISODISTORT server...')
        path = os.path.dirname(os.path.abspath(__file__))
        cif=find('hexMnTe.cif',path)
        options = {'basis11':'0', 'basis12':'-1','basis21':'1','basis22':'0'}
        fnameiso = os.path.join(path, "MnTe_iso.txt")
        pydistort.isoget.get(cif, fnameiso, options)
        f = open(fnameiso, 'r')
        lines = f.readlines()
        f.close()
        for idx, line in enumerate(lines):
            if 'mode definitions' in line:
                testIdx = int(1.0*idx)
        teststr = lines[testIdx + 5].strip()[:8]
        self.assertEqual(teststr, 'prm  !a5')

# End of class

if __name__ == '__main__':
    unittest.main()

# End of file
