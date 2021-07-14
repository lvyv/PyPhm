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
mqtt process module
=========================

An illustration of the rotation machine health model by viberation metric.
Exploring->Clustering->MDS->Predicting.
"""

# Author: Awen <26896225@qq.com>
# License: MIT

import logging
import paho.mqtt.client as mqtt


class MqttCliDaemon:
    topic_ = 'v1/devices/me/telemetry'
    client_ = None
    pipe_ = None

    # Constructor
    def __init__(self, pipe, clientid, host, port=1883, keepalive=60):
        self.pipe_ = pipe
        self.client_ = mqtt.Client()
        self.client_.username_pw_set(clientid)
        self.client_.connect(host, port, keepalive)
        self.client_.loop_start()

    # De-constructor
    def __del__(self):
        self.client_.loop_stop()
        self.client_.disconnect()
        self.client_ = None
        self.pipe_.close()
        self.pipe_ = None
        logging.info('Mqtt process exit.')

    # receive and publish data to iot
    def run(self):
        while True:
            data = self.pipe_.recv()
            # print(f'process:{data}')
            if data == "stop":
                logging.info(f'close pipe and exit.')
                self.pipe_.close()
                break
            # Sending data to iot
            sensor_data = data
            self.client_.publish(self.topic_, sensor_data, 1)


# 进程函数
def proc_mqtt(pi, tk, iot, port):
    try:
        svrobj = MqttCliDaemon(pi, tk, iot, port)
        svrobj.run()
        del svrobj
    except ConnectionRefusedError as cre:
        logging.info(cre)

