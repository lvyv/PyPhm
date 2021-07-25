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

import json
import logging
import unittest
import shutil
import phm.phm as phm
from datetime import datetime


class TestPhm(unittest.TestCase):
    """Tests for `phm` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_retrieve_url_file(self):
        """Test phm.retrieve_url_file."""
        # 1. OK condition file is there or can be download there
        ret = phm.retrieve_url_file('http://192.168.101.19:20080/archive/1st_test/1st_test/2003.10.23.05.04.13',
                                    '.cache/data/')
        self.assertTrue(ret == 200 or ret == -2)
        # 2. BAD URL
        ret = phm.retrieve_url_file('http://192.168.101.19:20080/archive/1st_test/1st_test/',
                                    '.cache/data/')
        self.assertTrue(ret == -3)
        # 3. New directory
        td = './tmp/'
        phm.mkdir_p(td)    # test phm function
        shutil.rmtree(td)
        ret = phm.retrieve_url_file('http://192.168.101.19:20080/archive/1st_test/1st_test/2003.10.23.05.04.13', td)
        self.assertTrue(ret, 200)

    def test_mqtt_publish(self):
        """Test phm.mqtt_publish."""
        # 本测试案例要求先推送一个文件wave_url到iot，按照要求的时间和设备号
        st = round(datetime.timestamp(datetime.strptime('2003-10-29T19:09:46', '%Y-%m-%dT%X')) * 1000)  # 缺省+08:00时区
        iot = '192.168.1.202'
        tok = 'ZOKriyQPgItNmPbtuxpo'  # 设备标识 iot的access token, Chiller-01
        sensor = {"ts": st, "values": {
            "wave_url": 'http://192.168.101.19:20080/archive/1st_test/1st_test/2003.10.29.19.09.46'
        }}
        phm.mqtt_publish(iot, 1883, tok, json.dumps(sensor))

    def test_get_iot_data(self):
        """Test phm.get_iot_data."""
        # 本测试案例要求先推送一个文件wave_url到iot，按照要求的时间和设备号
        # api要求timestamp，相对格林威治1970-01-01T00:00:00的总秒数，不会引起误会
        # 人类可读时间年月日时分秒，但默认了时区为东8区
        # python的timestamp是秒，js是毫秒
        # start_ = datetime.strptime('2008-05-22T20:26:31.383470+08:00', '%Y-%m-%dT%X.%f%z')
        # start_ = datetime.fromtimestamp(1209820000)  # 1209820400000(python is based on second while js is ms)
        # start_ = datetime.strftime(start_, '%Y-%m-%dT%X.%f%z')
        # delt_ = timedelta(hours=5)
        # st = '1 209 820 000 000' # 2008.05.03T21:06:40
        # et = '1 209 830 000 000'
        st = round(datetime.timestamp(datetime.strptime('2003-10-23T06:14:10', '%Y-%m-%dT%X')) * 1000)  # 缺省+08:00时区
        et = round(datetime.timestamp(datetime.strptime('2008-05-23T06:14:10', '%Y-%m-%dT%X')) * 1000)  # 缺省+08:00时区
        iot = '192.168.1.202'
        usr = 'user_battery@beidouapp.com'
        pwd = '12345'
        entitytype = 'DEVICE'
        entityid = 'e70e35a0-dd37-11eb-af5e-ebc2cd1145ee'
        tok = 'ZOKriyQPgItNmPbtuxpo'  # 设备标识 iot的access token, Chiller-01
        keys = 'wave_url,MDS'

        df = phm.get_iot_data(iot, usr, pwd, entitytype, entityid, keys, st, et)
        self.assertTrue(len(df) > 0)

    def test_cwru(self):
        """Test phm.get_iot_data."""
        param = 'http://192.168.101.19:8000/fault/105.mat'
        bpath = '../../phm-model/hvac/data/baseline/'
        df = phm.fre2mds(param, bpath)

    def test_ims(self):
        """Test phm.get_iot_data."""
        param = 'http://192.168.101.19:8000/2004.04.01.00.01.57'
        bpath = '../data/'
        df = phm.fre2mds(param, bpath)


if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestPhm('test_ims'))
    # suite.addTest(TestPhm('test_cwru'))
    unittest.TextTestRunner().run(suite)

