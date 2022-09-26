from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import io
import sys
import os

registers = {
    # Analog Gain:
    '0204': hex(1023)[2:].zfill(4),     # max. working 1023

    # Exposure time:
    '0202': '00A0',     # COARSE_INTEGRATION_TIME
}


def capture_frame(overwrite_registers=None, return_exposure_time=False, verbose=False):
    if overwrite_registers:
        for key, value in overwrite_registers.items():
            registers[key] = value

    if 'darwin' or 'linux' in sys.platform:
        registers_str = '\;'.join([f'{k},{v}' for k, v in registers.items()])
    else:
        registers_str = ';'.join([f'{k},{v}' for k, v in registers.items()])

    exposure_time = int(registers['0202'], base=16) * 12.74 / 1000000

    cmd = ['ssh',
           'exppi',
           '/home/pi/raspiraw/raspiraw',
           '-y 10',
           '-md 1',
           f'--regs "{registers_str}"',
           f'-t {exposure_time * 1000 + 500}',
           '-o /dev/stdout']

    if os.getenv('CMOSPI'):
        cmd = cmd[2:]

    if verbose:
        print(f'Expected exposure time is {exposure_time:.4f}s')
        print(' '.join(cmd))
        pipe_stderr = None
    else:
        pipe_stderr = PIPE

    process = Popen(' '.join(cmd), stdout=PIPE, stderr=pipe_stderr, shell=True)
    stdout, stderr = process.communicate()

    if verbose:
        print('Frame acquired')

    frame = stdout[:(3072 * 1520)]
    image_array = []

    with io.BytesIO(frame) as f:
        while True:
            row = f.read(3042)  # = 2028 * 12/8
            _ = f.read(30)  # Discard unused bits at the end of each row

            if not row:
                break

            while row:
                chunk = row[:3]
                row = row[3:]

                Pixel_1 = chunk[0] << 4 | (chunk[2] & 0b11110000) >> 4
                Pixel_2 = chunk[1] << 4 | (chunk[2] & 0b00001111)

                image_array += [Pixel_1, Pixel_2]

    np_image_array = np.array(image_array, dtype=np.uint16)
    np_image_array = np_image_array.reshape(1520, 2028)

    del image_array, frame, stdout

    if return_exposure_time:
        return np_image_array, exposure_time
    else:
        return np_image_array


if __name__ == '__main__':
    image = capture_frame(verbose=True)

    plt.imshow(image, cmap='gray', vmin=0, vmax=2**12 - 1)
    plt.show()