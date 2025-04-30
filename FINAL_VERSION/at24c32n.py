from eeprom import EEPROM
from machine import I2C, Pin

I2C_ADDR = 0x50     
EEPROM_SIZE = 32    


i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=800000)
eeprom = EEPROM(addr=I2C_ADDR, at24x=EEPROM_SIZE, i2c=i2c)


def save_device_states(r1, r2, r3):
    try:
        data = bytes([r1, r2, r3])
        eeprom.write(0, data) 
        print("All device states saved to EEPROM:", data)
    except Exception as e:
        print("Error saving to EEPROM:", e)
        

def load_device_states():
    try:
        data = eeprom.read(0, 3)  
        r1, r2, r3 = data
        print("All device states loaded from EEPROM:", data)
        return r1, r2, r3
    except Exception as e:
        print("EEPROM load error:", e)
        return 0, 0, 0