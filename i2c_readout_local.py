import pigpio

pi = pigpio.pi()
h = pi.i2c_open(10, 0x1A, 0)

#pi.i2c_write_device(h, [0x01, 0x40, 0x80])

pi.i2c_write_device(h, [0x02, 0x00])
count, data = pi.i2c_read_device(h, 2)

for byte in data:
    print(int.from_bytes(byte, 'big'))

pi.i2c_close(h)