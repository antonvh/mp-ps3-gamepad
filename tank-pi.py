#!/usr/bin/env python3

from ev3dev2.motor import Motor, OUTPUT_A, OUTPUT_B, OUTPUT_C
import struct

# Declare motors 
left_motor = Motor(OUTPUT_B)
right_motor = Motor(OUTPUT_C)

# Initialize variables. 
# Assuming sticks are in the middle when starting.
right_stick_x = 124
right_stick_y = 124

# A helper function for converting stick values (0 - 255)
# to more usable numbers (-100 - 100)
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
 
    val: float or int
    src: tuple
    dst: tuple
 
    example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def clamp(n, limits=(-100,100)):
    """
    Given a number and a range, return the number, or the extreme it 
    is closest to.

    :param n: number
    :return: number
    """
    (minn, maxn) = limits
    return max(min(maxn, n), minn)

# Find the PS3 Gamepad:
# /dev/input/event3 is the usual file handler for the gamepad.
# look at contents of /proc/bus/input/devices if it doesn't work.
# Find the line where it says 'Handlers'
infile_path = "/dev/input/event2"

# open file in binary mode
in_file = open(infile_path, "rb")

# Read from the file
# long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'    
EVENT_SIZE = struct.calcsize(FORMAT)
event = in_file.read(EVENT_SIZE)

while event:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)
    if ev_type == 3 and code == 3:
        right_stick_x = value
    if ev_type == 3 and code == 4:
        right_stick_y = value

    # Scale stick positions to -100,100
    forward = scale(right_stick_y, (0,255), (100,-100))
    left = scale(right_stick_x, (0,255), (100,-100))

    # Set motor voltages. If we're steering left, the left motor
    # must run backwards so it has a -left component
    # It has a forward component for going forward too. 
    left_motor.run_direct(duty_cycle_sp=clamp(forward - left))
    right_motor.run_direct(duty_cycle_sp=clamp(forward + left))

    # Finally, read another event
    event = in_file.read(EVENT_SIZE)

in_file.close()
