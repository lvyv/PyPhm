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
# start_ = datetime.strptime('2008-05-22T20:26:31.383470+08:00', '%Y-%m-%dT%X.%f%z')
start_ = datetime.fromtimestamp(1209820000)  # 1209820400000(python is based on second while js is ms)
# start_ = datetime.strftime(start_, '%Y-%m-%dT%X.%f%z')
delt_ = timedelta(hours=5)

app_ = FastAPI(
    title="装备健康管理模型",
    description="装备健康管理模型对外发布的RESTful API接口",
    version="2.2.0", )


class ComboIndicatorItem(BaseModel):
    reconnectmqtt: bool = True          # 是否每次重连mqtt，0为否
    obj: str = 'SOH'                    # 组合指标名称
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

    keys: str = 'wave_url,SOH'


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


@app_.post("/api/mdsdata")
async def mdsdata(item: ComboIndicatorItem):
    cmd = item.dict()
    # FIXME:要检查是否传入合适的obj,src,stime,etime
    cmd['command'] = 'comboindicator'

    ret = phm.fre2soh('http://127.0.0.1/archive/1st_test/1st_test/2003.10.23.00.14.13', '../phm-model/hvac/data/')
    # phm.compute_mdsdata('../phm-model/hvac/data/', 'http://127.0.0.1/archive/1st_test/1st_test/2003.10.23.00.14.13')
    jso = ret.to_json()
    # pipe_.send(json.dumps(cmd, default=defaultconverter))
    return {"status": "Command completed successfully.", 'SOH': jso}


@app_.post("/api/comboindicator")
async def comboindicator(item: ComboIndicatorItem):
    cmd = item.dict()
    # FIXME:要检查是否传入合适的obj,src,stime,etime
    cmd['command'] = 'comboindicator'
    pipe_.send(json.dumps(cmd, default=defaultconverter))
    return {"status": "Command completed successfully."}


# @app_.post("/api/setupmqtt")
async def setupmqtt(item: MqttItem):
    cmd = item.dict()
    # FIXME:要检查是否传入合适的host和token
    cmd['command'] = 'setupmqtt'
    pipe_.send(json.dumps(cmd))
    return {"status": "Command completed successfully."}


@app_.post("/api/kill")
async def kill():
    cmd = {"command": 'kill', "desc": 'A kill command from browser.'}
    pipe_.send(json.dumps(cmd))
    self_kill()
    return {"success": True}


# @app_.post("/api/postkv")
async def postkv(request: Request):
    cmd = await request.json()
    cmd['command'] = 'postkv'
    pipe_.send(json.dumps(cmd))
    return {"status": "Command is successfully posted."}


@app_.get("/")
async def root():
    return {"status": "Restful service is up."}


# 进程函数
def proc_rest(pi, pt=RSTport_):
    global pipe_
    pipe_ = pi
    run(pt)
