"""
Publisher wrapper around Paho MQTT Library
Allows ability to pause/resume publishing functionality
Limitations = publish only one topic
"""

import paho.mqtt.client as mqtt

from sim.utils.enums import MQTTPahoRC 
from sim.utils.constants import MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT

class MQTTPublisher(mqtt.Client):
    def __init__(self, publish_topic):
        mqtt.Client.__init__(self)
        self.topic = publish_topic
        self.msg_count = 0
        self._connected = False
        self._publishing = False

    def on_connect(self, mqttc, obj, flags, rc):
        if MQTTPahoRC(rc) == MQTTPahoRC.SUCCESS:
            self._connected = True
        else:
            print("ERROR: connection returned code= {}".format(MQTTPahoRC(rc)))

    def on_disconnect(self, mqttc, obj, rc):
        if MQTTPahoRC(rc) == MQTTPahoRC.SUCCESS:
            self._connected = False
            if self._publishing: 
                self._publishing = False
        else:
            print("ERROR: disconnection returned code= {}".format(MQTTPahoRC(rc)))

    def on_publish(self, mqttc, obj, mid):
        self.msg_count += 1

    def on_log(self, mqttc, obj, level, string):
        # print("LOG: {}".format(string))
        pass

    def stop_publish(self):
        self._publishing = False

    def start_publish(self):
        if not self._connected:
            connected = self.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
            if MQTTPahoRC(connected) == MQTTPahoRC.SUCCESS:    
                self._connected = True
        self._publishing = True
        
    def publish_topic(self, msg_contents) -> MQTTPahoRC:
        if self._publishing and self._connected:
            (rc, _) = self.publish(self.topic, msg_contents)
            return MQTTPahoRC(rc)
        else:
            return MQTTPahoRC.PUBLISHER_NOT_CONNECTED