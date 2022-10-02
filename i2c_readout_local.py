import pigpio

pi = pigpio.pi()
h = pi.i2c_open(10, 0x1A, 0)

pi.i2c_write_device(h, [0x01, 0x38, 0x01])

pi.i2c_write_device(h, [0x01, 0x3A])
count, data = pi.i2c_read_device(h, 1)

print(int.from_bytes(data, 'big', signed=True))

pi.i2c_close(h)