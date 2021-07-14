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

import json
import multiprocessing as mul
import phm.modules.mqttworker as mqttworker
import phm.modules.restworker as restworker
import phm.phm as phm
from phm import BENCHPATH
import logging


# setup and cache mqtt connection
def setup_mqtt(process, param):
    hst = param['host']
    tk = param['token']
    pt = param['port']

    (chB, chA) = mul.Pipe()
    if process:
        process.terminate()
        process.join()
    process = mul.Process(target=mqttworker.proc_mqtt, args=(chB, tk, hst, pt))
    process.start()
    process.chanel = lambda: None
    setattr(process.chanel, 'channel', chA)
    return process, chA


# 计算指标并推送
def compute_publish(process, channel, param):
    try:
        if process:
            # retidx = compute_indicator(param)
            retidx = phm.calculate_mds_indicator(param, BENCHPATH)
            if retidx:
                for item in retidx:
                    mds = {"ts": item['ts'], "values": {"MDS": item['MDS']}}
                    channel.send(json.dumps(mds))
        else:
            logging.info('Mqtt connectoin should be set and cache firstly.')
    except BrokenPipeError as be:
        logging.error(f'compute_publish to mqtt error.')
    return


if __name__ == "__main__":
    # prepare communication channels
    (endRE_B, endRE_A) = mul.Pipe()
    # init restful service
    rest_p = mul.Process(target=restworker.proc_rest, args=(endRE_B,))
    rest_p.start()
    # prepare mqtt service
    mqtt_p = None
    endMQ_A = None
    while True:
        data = endRE_A.recv()
        obj = json.loads(data)
        cmd = obj['command']
        if cmd == 'comboindicator':  # 根据观测值计算健康评估指标
            reconnect = obj['reconnectmqtt']
            if reconnect:
                (mqtt_p, endMQ_A) = setup_mqtt(mqtt_p, obj)
            compute_publish(mqtt_p, endMQ_A, obj)
        elif cmd == 'setupmqtt':  # 建立MQTT通道
            (mqtt_p, endMQ_A) = setup_mqtt(mqtt_p, obj)
            logging.info('Mqtt channel is set.', mqtt_p, endMQ_A)
        elif cmd == 'kill':
            logging.info(obj)
            break
        else:  # 异常情况
            if mqtt_p:
                endMQ_A.send('stop')
                mqtt_p.join()
                mqtt_p = None
            break

    logging.info('Main loop terminated, service exit.')
