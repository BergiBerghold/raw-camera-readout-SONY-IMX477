from subprocess import Popen, PIPE
import numpy as np
import os


def read_temperature():
    cmd = ['ssh',
           'vacpi',
           'python',
           '/home/pi/raw-camera-readout-SONY-IMX219/i2c_readout_local.py']

    process = Popen(cmd, stdout=PIPE)
    stdout, stderr = process.communicate()
    value = stdout.decode()

    temperature = np.interp(value, (0, 128), (-19, 80))
    temperature = round(temperature)

    return temperature


if __name__ == '__main__':
    print(f'Sensor temp is {read_temperature()} °C')

