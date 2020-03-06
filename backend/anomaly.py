#!/usr/bin/python3

import time
import serial
import serial.tools.list_ports

LINES = [
    #Hortizontal, y=3.4, x=0 to x=7.62
    (0, 3.4, 7.62)
]
TOLERANCE = 0
DEVIATE = 0
TOTAL = 0
F = open('logs/anomaly.log', 'w')

def run():
    global DEVIATE, TOTAL
    port = serial.Serial(serial.tools.list_ports.comports()[0].device, 115200)
    #time.sleep(2)
    #port.write(b'quit\r\n\r\n')
    #port.flush()
    #time.sleep(2)
    port.write(b'lep\n')
    port.flush()
    time.sleep(0.25)
    port.reset_input_buffer()
    print("Starting line {:.3f}x + {:.3f} to x={:.3f}".format(*LINES[0]))
    while True:
        avg = [0, 0, 0]
        count = 0
        while port.in_waiting:
            #print(port.in_waiting)
            data = port.read_until(size=port.in_waiting).decode().split(',')
            #print(data)
            if data[0] == "POS":
                data = (data[2],)+tuple(map(float, data[3:6]))
                #[identifier, x, y, z]
                for i in range(len(data)-1):
                    avg[i] += data[i+1]
                count += 1
        if not count:
            time.sleep(0.25)
            continue
        avg = tuple(map(lambda x: x/count, avg))
        intended = LINES[0][0] * avg[0] + LINES[0][1]
        DEVIATE += abs(avg[1]-intended)
        TOTAL += 1
        if abs(avg[1]-intended) > TOLERANCE:
            print("Anomaly detected! "+str(round(avg[1]-intended, 3))+" m off!")
            F.write("Anomaly detected! "+str(round(avg[1]-intended, 3))+" m off!\n")
        else:
            print("On track.")
            F.write("On track.\n")
            if avg[0] >= LINES[0][2]:
                del LINES[0]
                F.write("Line complete. Next {:.3f}x + {:.3f} to x={:.3f}".format(*LINES[0]))
                print("Line complete. Next {:.3f}x + {:.3f} to x={:.3f}".format(*LINES[0]))
                if not LINES:
                    return
        time.sleep(0.25)

try:
    run()
except KeyboardInterrupt:
    pass
print("Complete. Average deviation: {:.3f}".format(DEVIATE/TOTAL))
F.write("Complete. Average deviation: {:.3f}".format(DEVIATE/TOTAL))
F.close()
