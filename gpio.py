import esp32
import machine
from machine import Pin, Timer
import utime
from mqtt import*

# Pin Setup
R1 = Pin(26, Pin.OUT)
R2 = Pin(25, Pin.OUT)
R3 = Pin(33, Pin.OUT)

S_Led = Pin(4, Pin.OUT)

F1 = Pin(17, Pin.IN, Pin.PULL_DOWN)
F2 = Pin(18, Pin.IN, Pin.PULL_DOWN)
F3 = Pin(19, Pin.IN, Pin.PULL_DOWN)

Rst = Pin(32, Pin.IN, Pin.PULL_UP)

# Globals
last_trigger_times = {"F1": 0, "F2": 0, "F3": 0}
DEBOUNCE_DELAY = 400
debounce_timer = Timer(2)
reset_timer = Timer(1)

def reset_callback(timer):
    global press_start_time
    if Rst.value() == 0:
        print("Reset button held for 500ms! Clearing credentials and restarting.")
        hardReset()
        clear_wifi_credentials()
        time.sleep(5)
        machine.reset()

def handle_F1(pin):
    global last_trigger_times
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_trigger_times["F1"]) > DEBOUNCE_DELAY:
        last_trigger_times["F1"] = now
        debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_DELAY, callback=lambda t: process_F1())
        
def process_F1():
    new_state = not R1.value()
    R1.value(new_state)
    print("switch 1 toggled")
    publish_state()
    publish_deviceLog("device1", new_state)
    
def handle_F2(pin):
    global last_trigger_times
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_trigger_times["F2"]) > DEBOUNCE_DELAY:
        last_trigger_times["F2"] = now
        debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_DELAY, callback=lambda t: process_F2())

def process_F2():
    new_state = not R2.value()
    R2.value(new_state)
    print("Switch 2 toggled")
    publish_state()
    publish_deviceLog("device2", new_state)

def handle_F3(pin):
    global last_trigger_times
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_trigger_times["F3"]) > DEBOUNCE_DELAY:
        last_trigger_times["F3"] = now
        debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_DELAY, callback=lambda t: process_F3())

def process_F3():
    new_state = not R3.value()
    R3.value(new_state)
    print("Switch 3 toggled")
    publish_state()
    publish_deviceLog("device3", new_state)

# WiFi Reset
def Rst_irq_handler(pin):
    global press_start_time
    if pin.value() == 0:             
        press_start_time = time.ticks_ms()
        reset_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=reset_callback)

