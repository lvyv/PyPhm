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
restful process module
=========================

An illustration of the rotation machine health model by viberation metric.
Exploring->Clustering->MDS->Predicting.
"""

# Author: Awen <26896225@qq.com>
# License: MIT

import os
import psutil
import json
import uvicorn
import phm as phm

from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from typing import Optional
from pydantic import BaseModel

###############################
# global configuration section
#
RSTport_ = 29054                                    # 模型微服务监听端口

IOTmqpt_ = 1883                                     # 物联网mqtt端口
IOTuri_ = '192.168.1.202:8090'                      # 物联网http地址及端口
IOTusr_ = 'user_battery@beidouapp.com'              # 物联网用户
IOTpwd_ = '12345'                                   # 物联网密码
IOTdev_ = 'e70e35a0-dd37-11eb-af5e-ebc2cd1145ee'    # 设备标识 iot的device id, Chiller-01
IOTtok_ = 'ZOKriyQPgItNmPbtuxpo'                    # 设备标识 iot的access token, Chiller-01
###############################

# default value for convenience
pipe_ = None
start_ = datetime.fromtimestamp(1209820000)  # 1209820400000(python is based on second while js is ms)
delt_ = timedelta(hours=5)

app_ = FastAPI(
    title="装备健康管理模型",
    description="装备健康管理模型对外发布的RESTful API接口",
    version="2.2.0", )


class ComboIndicatorItem(BaseModel):
    reconnectmqtt: bool = True          # 是否每次重连mqtt，0为否
    obj: str = 'MDS'                    # 组合指标名称
    stime: datetime = start_            # 时间窗口起点
    etime: datetime = start_ + delt_    # 时间窗口终点
    iot: str = IOTuri_
    usr: str = IOTusr_
    pwd: str = IOTpwd_
    entitytype: str = 'DEVICE'
    entityid: str = IOTdev_

    host: str = IOTuri_.split(':')[0]   # 物联网MQTT服务器地址
    token: str = IOTtok_
    port: Optional[int] = IOTmqpt_

    keys: str = 'wave_url,MDS'


class MqttItem(BaseModel):
    host: str = IOTuri_.split(':')[0]             # 物联网MQTT服务器地址
    token: str = IOTtok_
    port: Optional[int] = IOTmqpt_


def self_kill():
    process = psutil.Process(os.getpid())
    parent = process.parent()
    if process:
        process.kill()
    if parent:
        parent.kill()
    return


def defaultconverter(o):
    if isinstance(o, datetime):
        return o.isoformat()  # __str__()


# receive and publish data to iot
def run(pt):
    uvicorn.run(app_, host="0.0.0.0", port=pt)


@app_.post("/api/comboindicator")
async def comboindicator(item: ComboIndicatorItem):
    cmd = item.dict()
    # FIXME:要检查是否传入合适的obj,src,stime,etime
    cmd['command'] = 'comboindicator'
    pipe_.send(json.dumps(cmd, default=defaultconverter))
    return {"status": "Async command successfully issued."}


@app_.post("/api/kill")
async def kill():
    cmd = {"command": 'kill', "desc": 'A kill command from browser.'}
    pipe_.send(json.dumps(cmd))
    self_kill()
    return {"Success": True}


@app_.get("/")
async def root():
    return {"status": "Restful service is up."}


# 进程函数
def proc_rest(pi, pt=RSTport_):
    global pipe_
    pipe_ = pi
    run(pt)
