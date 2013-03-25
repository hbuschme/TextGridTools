# -*- coding: utf-8 -*-

# TextGridTools -- Read, write, and manipulate Praat TextGrid files
# Copyright (C) 2013 Hendrik Buschmeier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# RUN as 'python -m tgt.tests.run'

import unittest

from . import test_core

test_modules = [
    test_core
]


def main():
    package_test_suite = unittest.TestSuite()
    for test_module in test_modules:
        module_test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
        package_test_suite.addTest(module_test_suite)
    runner = unittest.TextTestRunner()
    runner.run(package_test_suite)


if __name__ == '__main__':
    main()
