from analogio import AnalogIn
import time
import board

sensor = AnalogIn(board.A10)

dry = 40000
wet = 25000

while True:
    adc = sensor.value
    print("Moisture: %0.1f " % adc)
    if adc >= dry:
        print("Soil is dry")
    elif adc <= wet:
        print("Soil is wet")
    else:
        print("Soil is good")
    time.sleep(5)