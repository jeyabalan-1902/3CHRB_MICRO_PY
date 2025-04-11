import esp32
from umqtt.simple import MQTTClient
import ujson
import ntptime
import time
import ubinascii
import urandom
import machine
import utime
from collections import OrderedDict
from machine import Timer, Pin
import uasyncio as asyncio
from nvs import get_product_id, product_key, clear_wifi_credentials
from gpio import R1,R2,R3


client = None
product_id = get_product_id()

BROKER_ADDRESS = "mqtt.onwords.in"
MQTT_CLIENT_ID = product_id
TOPIC_SUB = f"onwords/{product_id}/status"
TOPIC_SUB1 = f"onwords/{product_id}/getCurrentStatus"
TOPIC_SOFTRST = f"onwords/{product_id}/softReset"
TOPIC_PUB = f"onwords/{product_id}/currentStatus"
PORT = 1883
USERNAME = "Nikhil"
MQTT_PASSWORD = "Nikhil8182"
MQTT_KEEPALIVE = 60

def hardReset():
    global client
    if client is None:
        print("MQTT client not initialized. Cannot publish hard reset message.")
    else:
        try:
            payload = {"id": product_id}
            client.publish("onwords/hardReset", ujson.dumps(payload))
            print("Hard reset published to MQTT broker.")
        except Exception as e:
            print(f"Failed to publish hard reset message: {e}")

#publish devices state
def publish_state():
    global client
    if client:
        state = {
            "device1": R1.value(),
            "device2": R2.value(),
            "device3": R3.value()
        }

        client.publish(TOPIC_PUB, ujson.dumps(state))
        print("Published state:", state)
    else:
        print("MQTT client not connected!")
 
 
#publish Device log
def publish_deviceLog(device, state):
    global client
    if client:
        log = {
            device: state,
            "id": product_id,
            "client_id": "Switch",
            "ip": network.WLAN(network.STA_IF).ifconfig()[0],
            "time_stamp": get_timestamp()
        }
        client.publish(f"onwords/{product_id}/switch", ujson.dumps(log))
        print("log published:", log)       
    else:
        print("mqtt client not connected")

#MQTT callback
def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    print(f"Received from {topic_str}: {msg.decode()}")

    if topic_str == f"onwords/{product_id}/status":
        try:
            data = ujson.loads(msg)

            if "device1" in data and data["device1"] in [0, 1]:
                R1.value(data["device1"])
                status_msg = ujson.dumps({"device1": data["device1"]})
                client.publish(TOPIC_PUB, status_msg)

            if "device2" in data and data["device2"] in [0, 1]:
                R2.value(data["device2"])
                status_msg = ujson.dumps({"device2": data["device2"]})
                client.publish(TOPIC_PUB, status_msg)

            if "device3" in data and data["device3"] in [0, 1]:
                R3.value(data["device3"])
                status_msg = ujson.dumps({"device3": data["device3"]})
                client.publish(TOPIC_PUB, status_msg)

        except ValueError as e:
            print("Error parsing JSON:", e)

    if topic_str == f"onwords/{product_id}/getCurrentStatus":
        try:
            publish_state()

        except ValueError as e:
            print("Error parsing JSON:", e)

    if topic_str == f"onwords/{product_id}/softReset":
        try:
            clear_wifi_credentials()
            state = {
                "status": True
            }
            client.publish(TOPIC_SOFTRST, ujson.dumps(state))
            time.sleep(5)
            machine.reset()

        except ValueError as e:
            print("Error:", e)

#Connect MQTT
def connect_mqtt():
    global client
    try:
        client = MQTTClient(client_id=product_key, server=BROKER_ADDRESS, port=PORT, user=USERNAME, password=MQTT_PASSWORD, keepalive=MQTT_KEEPALIVE)
        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(TOPIC_SUB)
        client.subscribe(TOPIC_SUB1)
        client.subscribe(TOPIC_SOFTRST)
        print(f"Subscribed to {TOPIC_SUB}")
        return client
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return None

#Reconnect MQTT
def reconnect_mqtt():
    global client
    print("Reconnecting MQTT...")
    try:
        if client:
            client.disconnect()
    except:
        pass
    client = None
    await asyncio.sleep(2)  
    return connect_mqtt()

#MQTT Listen
async def mqtt_listener():
    while True:
        try:
            if client:
                client.check_msg()
        except Exception as e:
            print("Error checking MQTT:", e)
            await reconnect_mqtt()
        await asyncio.sleep(0.1)

#keep alive
async def mqtt_keepalive():
    while True:
        try:
            if client:
                print("Sending MQTT PINGREQ")
                client.ping() 
        except Exception as e:
            print("MQTT Keep-Alive failed:", e)
            await reconnect_mqtt()
        await asyncio.sleep(MQTT_KEEPALIVE // 2)