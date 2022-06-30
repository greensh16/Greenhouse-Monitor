import time
import board
import wifi
import adafruit_shtc3
import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Get wifi details from the secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# WiFi
try:
    print("Connecting to %s" % secrets["ssid"])
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print("Connected to %s!" % secrets["ssid"])
# Wi-Fi connectivity fails with error messages, not specific errors, so this except is broad.
except Exception as e:
    print("Failed to connect to WiFi. Error:", e, "\nBoard will hard reset in 30 seconds.")
    time.sleep(30)
    microcontroller.reset()

def connect(mqtt_client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print("Flags: {0}\n RC: {1}".format(flags, rc))


def disconnect(mqtt_client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client publishes data to a feed.
    print("Published to {0} with PID {1}".format(topic, pid))


def message(client, topic, message):
    # Method called when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

mqtt_client = MQTT.MQTT(
    broker=secrets["mqtt-broker"],
    port=1883,
    username=secrets["user"],
    password=secrets["pass"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
mqtt_client.connect()

i2c = board.I2C()  # uses board.SCL and board.SDA
sht = adafruit_shtc3.SHTC3(i2c)

while True:
    temperature, relative_humidity = sht.measurements
    print("Temperature: %0.1f C" % temperature)
    print("Humidity: %0.1f %%" % relative_humidity)
    print("")
    
    try:
        mqtt_client.loop()
        mqtt_client.publish("homeassistant/sensor/shtc3_temp", temperature)
        time.sleep(30)
    except Exception as err:
        print("An error occured: {}".format(err))
        wifi.reset()
        wifi.connect()
        mqtt_client.reconnect()
