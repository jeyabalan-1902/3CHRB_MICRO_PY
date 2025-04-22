from machine import I2C, Pin
import time


i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
EEPROM_ADDR = 0x50  

def save_state(r1, r2, r3):
    state = bytes([r1, r2, r3])
    data = bytes([0x00, 0x00]) + state  
    i2c.writeto(EEPROM_ADDR, data)
    print("Relay state saved to EEPROM:", state)

def load_state():
    i2c.writeto(EEPROM_ADDR, bytes([0x00, 0x00])) 
    state = i2c.readfrom(EEPROM_ADDR, 3)
    print("Relay state loaded from EEPROM:", state)
    return state[0], state[1], state[2]
