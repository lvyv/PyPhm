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
        print('Mqtt process exit.')

    # receive and publish data to iot
    def run(self):
        while True:
            data = self.pipe_.recv()
            # print(f'process:{data}')
            if data == "stop":
                print(f'close pipe and exit.')
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
        print(cre)

