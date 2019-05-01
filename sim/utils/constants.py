# Mosquittoe server
MOSQUITTO_SERVER = "127.0.0.1"
MOSQUITTO_PORT = 1883
MOSQUITTO_TIMEOUT = 60  # [s]

# Publishing frequencies
BASIC_SENSOR_DETECTION_FREQ = 2   # [Hz]
MOVE_COMMAND_FREQ = 1   # [Hz]

# InfluxDB 
INFLUXDB_USER = 'root'
INFLUXDB_PW = 'root'
INFLUXDB_DBNAME = 'robot'
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086

# Grafana
GRAFANA_HOST = 'localhost'
GRAFANA_PORT = 3000