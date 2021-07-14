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

参考:
  - [1]Neupane D, Seok J. Bearing fault detection and diagnosis using case western reserve university
  dataset with deep learning approaches: A review[J]. IEEE Access, 2020, 8: 93155-93178.
"""

# Author: Awen <26896225@qq.com>
# License: MIT

import json
import logging
import unittest
import shutil
import matplotlib.pyplot as plt
import phm.phm as phm
from adjustText import adjust_text
from matplotlib import patches as mpatches
from os import listdir
from os.path import isfile, join
from phm.modules import utils
from phm.vibration import cluster, mds
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


def analysis_ims():
    mypath = '../../phm-model/hvac/data/'  # 'data/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # Set figure size for matplotlib
    plt.rcParams['figure.figsize'] = [12, 6]
    files = onlyfiles  # [0:6]

    data = []
    for file in files:
        x = utils.load_dat(file, mypath)
        data.append(x[0])

    sr = 20480  # sample rate
    ws = 2048  # window size
    freqs, spectra = cluster.ts2fft(data, sr, ws)
    cluster_, df = cluster.cluster_vectors(spectra, False)

    # plot frequencies cluster chart
    fig, ax = plt.subplots()
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
    ax.set_title('Frequency Domain Representation of Each Signal')
    for idx, elem in enumerate(df['vectors']):
        for el in elem:
            ax.plot(freqs, spectra[el], c=df['color'][idx])
    plt.show()

    df2 = mds.dev_age_compute(spectra, freqs, [28, 12, 52])
    pos = mds.compute_mds_pos(spectra)
    # set color for each points in df2
    df2.loc[:, 'color'] = '#000000'
    for idx, elems in enumerate(df['vectors']):
        for el in elems:
            df2.loc[el, 'color'] = df.loc[idx, 'color']

    # plot mds scatter chart
    plt.figure(1)
    plt.axes([0., 0., 1., 1.])
    plt.scatter(pos[:, 0], pos[:, 1], marker='.', edgecolors=df2.loc[:, 'color'], s=df2.loc[:, 'age'],
                facecolors='none',
                alpha=0.5, lw=1, label=df2.loc[:, 'color'])
    hnds = []
    for idx, el in enumerate(df['color']):
        pop = mpatches.Patch(color=el, label=f'cluster:{df["cid"][idx]}, {df["vectors"][idx]}')
        hnds.append(pop)
    plt.legend(handles=hnds, prop={'size': 6})
    txts = df[df['cid'] == -1]['vectors'][0]  # -1 point.
    texts = [plt.text(pos[txt, 0], pos[txt, 1], txt) for txt in txts]
    adjust_text(texts)
    plt.show()
    return


if __name__ == "__main__":
    unittest.main()
    # analysis_ims()
    # analysis_cwru()
