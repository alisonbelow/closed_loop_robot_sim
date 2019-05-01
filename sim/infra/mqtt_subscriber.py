"""
Subscriber wrapper around Paho MQTT Library
Abstracts away concept of loop()
Allows ability to pause/resume subscription functionality
Limitations = publish only one topic
"""

import paho.mqtt.client as mqtt

from sim.utils.constants import MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT
from sim.utils.enums import MQTTPahoRC 

class MQTTSubscriber(mqtt.Client):
    def __init__(self, subscribe_topic):
        mqtt.Client.__init__(self)
        self.topic = subscribe_topic
        self._connected = False
        self._subscribed = False

    def on_connect(self, mqttc, obj, flags, rc):
        if MQTTPahoRC(rc) == MQTTPahoRC.SUCCESS:
            print("Connected OK")
            self._connected = True
        else:
            print("ERROR: connection returned code= {}".format(MQTTPahoRC(rc)))

    def on_disconnect(self, mqttc, obj, rc):
        if MQTTPahoRC(rc) == MQTTPahoRC.SUCCESS:
            print("Disconnect OK")
            self._connected = False
            print("self._connected = {}".format(self._connected))
            if self._subscribed: 
                self.unsubscribe()
        else:
            print("ERROR: disconnection returned code= {}".format(MQTTPahoRC(rc)))

    def on_message(self, mqttc, obj, msg):
        print("{} #{}: {} {}".format(msg.topic, self.msg_count, msg.qos, msg.payload))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: ID={} {}".format(mid, granted_qos))
        self._subscribed = True

    def on_log(self, mqttc, obj, level, string):
        print("LOG: {}".format(string))

    def subscribe_topic(self, callback_fxn):
        connected = self.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
        if MQTTPahoRC(connected) == MQTTPahoRC.SUCCESS:    
            self._connected = True
        
        # TODO do not subscibe if not connected

        (subscribed, _) = self.subscribe(self.topic)
        if MQTTPahoRC(subscribed)  == MQTTPahoRC.SUCCESS:    
            self._subscribed = True
        
        self.message_callback_add(self.topic, callback_fxn)
        self.loop_start()

    def unsubscribe(self):
        print("Unsubscribe")
        self.loop_stop()
        self._subscribed = False

    def resubscribe(self):
        print("Resubscribe")
        self._subscribed = True
        self.loop_start()
        

