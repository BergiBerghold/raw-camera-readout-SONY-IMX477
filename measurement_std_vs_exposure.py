from capture_frame import capture_frame
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys, os


# Create Directory for Data

try:
    measurement_name = sys.argv[1]
except:
    measurement_name = 'run'

timestamp = datetime.now().strftime('%d.%m._%H:%M:%S')
measurement_directory = f'measurements/{measurement_name}_{timestamp}'
os.makedirs(measurement_directory)

type_of_measurement = os.path.basename(__file__)[:-3]
open(f'{measurement_directory}/{type_of_measurement}', 'w').close()


# Create CSV file for data points

header = ['Exposure Time', 'Gain', 'Median of STD', 'Mean of STD']
df = pd.DataFrame(columns=header)
df.to_csv(f'{measurement_directory}/datapoints.csv', mode='w', index=False, header=True)

registers = {
    # Analog Gain:
    '0204': hex(1023)[2:].zfill(4),     # max. working 1023

    # Exposure time:
    '0202': '00A0',     # COARSE_INTEGRATION_TIME
}

for gain in list(range(0, 1023, 32)) + [1023]:
    gain_hex = hex(gain)[2:].zfill(4)
    registers['0204'] = gain_hex

    for exposure in list(range(0, 65535, 5000)) + [65535]:
        exposure_hex = hex(exposure)[2:].zfill(4)
        registers['0202'] = exposure_hex

        frames = np.zeros((1520, 2028, 10), dtype=np.int16)

        for idx in range(10):
            frame, exposure_time = capture_frame(overwrite_registers=registers, return_exposure_time=True)
            frames[:, :, idx] = frame

        standard_dev = np.std(frames, axis=2)
        median = np.median(standard_dev)
        mean = np.mean(standard_dev)

        del frames, frame, standard_dev

        data_entry = [exposure_time, gain, median, mean]
        df = pd.DataFrame([data_entry])
        df.to_csv(f'{measurement_directory}/datapoints.csv', mode='a', index=False, header=False)

        print(f'STD acquired for exposure time {exposure_time} and gain {gain}. STD is {median}')
