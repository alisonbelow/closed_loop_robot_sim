## Features still remaining

1. Actual sensor simulation, using dummy sensor that automatically gives robot global pose
2. Fix grafana dashboard to show Y error, not just the X/Y/Z position output from sensor
3. Controller should accept configuration of sensors. Should come from json config file fed into `main.py`. Sensors should be instantiated in this way, not manually in `main.py`.
4. REST endpoint in form of Flask server to catch webhook from Grafana button press for controller state toggling.  
    Scipt should look something like this:

    ```python
    import json
    from flask import Flask
    from flask import request
    from flask_httpauth import HTTPBasicAuth
    import paho.mqtt.client as mqtt

    from sim.infra.topic_utils import gen_influxdb_time
    from sim.utils.constants import MOSQUITTO_PORT, MOSQUITTO_SERVER, MOSQUITTO_TIMEOUT, GRAFANA_HOST, GRAFANA_PORT
    from sim.utils.enums import ObjState

    app = Flask(__name__)
    mqtt_client = mqtt.Client()

    STATE_ON = json.dumps({
        "time": gen_influxdb_time(),
        "control_state": ObjState.ON.value
    })
    STATE_OFF = json.dumps({ 
        "time": gen_influxdb_time(),
        "control_state": ObjState.OFF.value
    })

    @app.route('/statechange', methods=['POST'])
    def state_change():
        client.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
        data = json.loads(request.data.decode('utf-8'))
        if data['state'] == 'off':
            client.publish(topic="controller/state", payload=STATE_OFF)
        elif data['state'] == 'on':
            client.publish(topic="controller/state", payload=STATE_ON)

        client.disconnect()

    if __name__ == "__main__":
        app.run(host='0.0.0.0')
    ```

## Bugs to Fix

1. Better thread joining for publisher for controller and sensor - done to make sure it works, but should be accounted for in all types of exits/breaks
2. Need to have Grafana/InfluxDB information generated persist through open/close of Docker container. Currently have issue where if I link these locations during docker run, the permissions do not work and I am unable to re-open the container with all Grafana and InfluxDB server running.
3. Math is wrong in controller computation of move command - some issue with x/z resulting from how open loop vs closed loop computation of next move is done. Needs some testing to figure out what is wrong.