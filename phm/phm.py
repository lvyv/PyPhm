# Copyright 2021 The CASICloud Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# pylint: disable=invalid-name
# pylint: disable=missing-docstring

"""
=========================
phm module
=========================

An illustration of the rotation machine health model by viberation metric.
Exploring->Clustering->MDS->Predicting.
"""

# Author: Awen <26896225@qq.com>
# License: MIT


import logging
import unittest


def calculate_mds_indicator(modelparam, bp='./data/'):
    idx = None
    try:
        idx = [{"ts": 1626265933639, "MDS": '{"key1": 1, "key2": 2}'}]
    except ValueError as ve:
        logging.error('Exception occured.', ve)
        pass
    return idx


class Tests(unittest.TestCase):
    def testCache(self):
        self.assert_(True)


if __name__ == "__main__":
    unittest.main()
