from micropython import const
import asyncio
import aioble
import bluetooth
import struct
import machine
import ujson
from machine import Pin
from gpio import R1, R2, R3
from mqtt import publish_state, publish_ble_deviceLog


_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_SENSOR_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
_BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')

_ADV_INTERVAL_MS = 250_000


ble_service = aioble.Service(_BLE_SERVICE_UUID)
led_characteristic = aioble.Characteristic(ble_service, _BLE_LED_UUID, read=True, write=True, notify=True, capture=True)

aioble.register_services(ble_service)


async def ble_peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="3CHRB-BLE",
                services=[_BLE_SERVICE_UUID],
                ) as connection:
                    print("Connection from", connection.device)
                    await connection.disconnected()             
        except asyncio.CancelledError:
            print("Peripheral task cancelled")
        except Exception as e:
            print("Error in ble_task:", e)
        finally:
            await asyncio.sleep_ms(100)
            
            
async def wait_for_write():
    while True:
        try:
            connection, data = await led_characteristic.written()
            print("BLE Data Received:", data)
            payload = ujson.loads(data.decode())
            if "device1" in payload:
                if payload["device1"] == 1:
                    new_state = not R1.value()
                    R1.value(new_state)
                else:
                    new_state = not R1.value()
                    R1.value(new_state)
                publish_ble_deviceLog("device1", R1.value())
                publish_state()
            if "device2" in payload:
                if payload["device2"] == 1:
                    new_state = not R2.value()
                    R2.value(new_state)
                else:
                    new_state = not R2.value()
                    R2.value(new_state)
                publish_ble_deviceLog("device2", R2.value())
                publish_state()
            if "device3" in payload:
                if payload["device3"] == 1:
                    new_state = not R3.value()
                    R3.value(new_state)
                else:
                    new_state = not R3.value()
                    R3.value(new_state)
                publish_ble_deviceLog("device3", R3.value())
                publish_state()
               
        except asyncio.CancelledError:
            print("Peripheral task cancelled")
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            await asyncio.sleep_ms(100)


