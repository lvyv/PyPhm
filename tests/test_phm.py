#!/usr/bin/env python
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
"""旋转机械健康管理模型.
单元测试模块

"""

# Author: Awen <26896225@qq.com>
# License: MIT

import unittest
import phm.phm as phm


class TestPhm(unittest.TestCase):
    """Tests for `phm` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_calculate_mds_indicator(self):
        """Test phm.retrieve_url_file."""
        modelparam = {"key1": 1}
        retidx = phm.calculate_mds_indicator(modelparam)
        for item in retidx:
            self.assertTrue(isinstance(item['MDS'], str))


if __name__ == "__main__":
    unittest.main()

