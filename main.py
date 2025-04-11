import esp32
import network
import ujson
import usocket
import usocket as socket
import ntptime
import time
import ubinascii
import urandom
import machine
import utime
from collections import OrderedDict
from machine import Pin, disable_irq, enable_irq, Timer
from time import sleep_ms
import uasyncio as asyncio
import struct

from machine import Pin, Timer
from nvs import get_product_id, get_stored_wifi_credentials
from wifi_con import connect_wifi, check_internet, wifi, ap
from http import start_http_server
from mqtt import mqtt_listener, mqtt_keepalive, connect_mqtt
from gpio import handle_F1, handle_F2, handle_F3, Rst_irq_handler, F1, F2, F3, Rst
import mqtt

product_id = get_product_id()
print(f"stored Product ID:{product_id}")

F1.irq(trigger=Pin.IRQ_RISING, handler=handle_F1)
F2.irq(trigger=Pin.IRQ_RISING, handler=handle_F2)
F3.irq(trigger=Pin.IRQ_RISING, handler=handle_F3)
Rst.irq(trigger=Pin.IRQ_FALLING, handler=Rst_irq_handler)

async def wifi_reconnect():
    retry_count = 0
    while True:
        if not wifi.isconnected():
            print("Wi-Fi disconnected! Attempting reconnection...")
            stored_ssid, stored_password = get_stored_wifi_credentials()

            if stored_ssid and stored_password:
                while retry_count < 15:
                    print(f"Reconnection attempt {retry_count + 1} of {MAX_FAST_RETRIES}...")
                    if connect_wifi(stored_ssid, stored_password):
                        print("Wi-Fi Reconnected!")
                        retry_count = 0  
                        break
                    retry_count += 1
                    await asyncio.sleep(10)

                if not wifi.isconnected():
                    print("Switching to slow reconnection attempts every 5 minutes.")
                    while not wifi.isconnected():
                        if connect_wifi(stored_ssid, stored_password):
                            print("Wi-Fi Reconnected!")
                            retry_count = 0 
                            break
                        print("Reconnection failed, retrying in 5 minutes...")
                        await asyncio.sleep(300)
            else:
                print("No stored Wi-Fi credentials. Restarting HTTP server...")
                await start_http_server()
        else:
            if not check_internet():
                print("Wi-Fi connected but no internet access. Reconnecting Wi-Fi...")
                wifi.disconnect()  
                await asyncio.sleep(5)  
            else:
                print("Wi-Fi and internet are connected.")
                await asyncio.sleep(10) 
        
async def main():
    stored_ssid, stored_password = get_stored_wifi_credentials()
    if stored_ssid and stored_password:
        ap.active(False)
        while True: 
            if connect_wifi(stored_ssid, stored_password):
                if check_internet():
                    print("Wi-Fi and internet are connected. Connecting to MQTT broker...")
                    connect_mqtt()
                    t1 = asyncio.create_task(mqtt_listener())
                    t2 = asyncio.create_task(mqtt_keepalive())
                    t3 = asyncio.create_task(wifi_reconnect())
                    await asyncio.gather(t1, t2, t3)
                    break 
                else:
                    print("Wi-Fi connected but no internet access. Reconnecting Wi-Fi...")
                    wifi.disconnect() 
                    await asyncio.sleep(5)  
            else:
                print("Failed to connect to Wi-Fi. Retrying in 10 seconds...")
                await asyncio.sleep(10)        
            
    else:
        print("No WiFi credentials found, starting HTTP server...")
        await start_http_server()

if __name__ == "__main__":
    asyncio.run(main())