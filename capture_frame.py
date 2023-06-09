from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import io
import sys
import os

registers = {
    # Analog Gain:
    '0204': hex(1)[2:].zfill(4),     # max. working 1023

    # Exposure time:
    '0202': '0008',     # COARSE_INTEGRATION_TIME
    '0342': 'FFFF',     # LINE_LENGTH_PCK               default 31C4
    '3100': '00',       # Shift Register?
}


def capture_frame(overwrite_registers=None, return_exposure_time=False, verbose=False):
    if overwrite_registers:
        for key, value in overwrite_registers.items():
            registers[key] = value

    if 'darwin' or 'linux' in sys.platform:
        registers_str = '\;'.join([f'{k},{v}' for k, v in registers.items()])
    else:
        registers_str = ';'.join([f'{k},{v}' for k, v in registers.items()])

    FINE_INTEG_Time = 1936
    IVTPXCK_period = 1 / (250 * 10 ** 6)

    LINE_LENGTH_PCK = int(registers['0342'], base=16)
    COARSE_INTEGRATION_TIME = int(registers['0202'], base=16)
    SHIFT = int(registers['3100'], base=16)

    COARSE_INTEGRATION_TIME *= 2**(SHIFT)

    Tline = LINE_LENGTH_PCK * IVTPXCK_period / 4
    exposure_time = Tline * (COARSE_INTEGRATION_TIME + FINE_INTEG_Time / LINE_LENGTH_PCK)

    cmd = ['ssh',
           'vacpi',
           '/home/pi/raspiraw_hermann/raspiraw',
           '-y 10',
           f'--regs "{registers_str}"',
           f'-t {int(exposure_time * 1000 + 1000)}',
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
        print(f'Frame acquired')

    frame = stdout[:(6112 * 3040)]
    image_array = []

    with io.BytesIO(frame) as f:
        while True:
            row = f.read(6084)  # = 4056 * 12/8
            _ = f.read(28)  # Discard unused bits at the end of each row

            if not row:
                break

            while row:
                chunk = row[:3]
                row = row[3:]

                Pixel_1 = chunk[0] << 4 | (chunk[2] & 0b11110000) >> 4
                Pixel_2 = chunk[1] << 4 | (chunk[2] & 0b00001111)

                image_array += [Pixel_1, Pixel_2]

    np_image_array = np.array(image_array, dtype=np.uint16)
    np_image_array = np_image_array.reshape(3040, 4056)

    del image_array, frame, stdout

    if return_exposure_time:
        return np_image_array, exposure_time
    else:
        return np_image_array


if __name__ == '__main__':
    image = capture_frame(verbose=True)

    plt.imshow(image, cmap='gray', vmin=0, vmax=2**12 - 1)
    plt.show()

    #test