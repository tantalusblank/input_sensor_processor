
from logging import exception
from datetime import datetime

# Script Options

# Sets whether the log file clears each time the script runs:
clear_logs_on_run = True

# Sets whether the script continues to run after loading the input file:
continuous_mode = False

# Import file (leave blank to skip import):
sensor_data_file = 'dist/device_data.bin'

# Input sensors
device00 = [1, 4, 4, 1]
device01 = [1, 4, 1, 1]




def determine_sensor(bufferdata, device):
    pos1 = device[0]*2
    pos2 = pos1 + device[1]*2
    pos3 = pos2 + device[2]*2
    pos4 = pos3 + device[3]*2

    extracted_data1 = bufferdata[:pos1]
    extracted_data2 = int(bufferdata[pos1:pos2], 16)
    extracted_data3 = int(bufferdata[pos2:pos3], 16)
    extracted_data4 = int(bufferdata[pos3:pos4], 16)


class SensorDatapacket:

    num_of_packets = 0

    def __init__(self, packet_type, timestamp_mil_sec, error):
        self.packet_type = packet_type
        self.timestamp_mil_sec = timestamp_mil_sec
        self.error = error

        SensorDatapacket.num_of_packets += 1

    def timestamp_sec(self):
        if self.timestamp_mil_sec > 0:
            return int(self.timestamp_mil_sec / 1000)
        else:
            return self.timestamp_mil_sec

    def detect_error(self):
        if (err >= 256):
            exception("OH NO")

class TempSensorDatapacket(SensorDatapacket):
    def __init__(self, packet_type, timestamp_mil_sec, error, temp_mil_deg):
        super().__init__(packet_type, timestamp_mil_sec, error)
        self.temp_mil_deg = temp_mil_deg

    def __repr__(self):
        return "{}, {}, {}, {}, {}, {}".format(
            self.packet_type,
            self.timestamp_mil_sec,
            self.timestamp_sec(),
            self.error,
            self.temp_mil_deg,
            self.temp_deg())

    def temp_deg(self):
        if self.temp_mil_deg > 0:
            return int(self.temp_mil_deg / 1000)
        else:
            return self.temp_mil_deg

class BinarySensorDatapacket(SensorDatapacket):
    def __init__(self, packet_type, timestamp_mil_sec, error, bin_state):
        super().__init__(packet_type, timestamp_mil_sec, error)
        self.binary_state = bin_state

    def __repr__(self):
        return "{}, {}, {}, {}, {}".format(
                                        self.packet_type,
                                        self.timestamp_mil_sec,
                                        self.timestamp_sec(),
                                        self.error,
                                        self.binary_state)

def log_output(sensor_packet):
    with open('logs.txt', 'a') as logfile:
        logfile.writelines(str(datetime.now()) + ', ' + str(sensor_packet) + '\n')


# Open the file and read binary contents into a variable

if clear_logs_on_run == True:
    with open('logs.txt', 'w') as logfile:
        logfile.write('')

with open(sensor_data_file, 'rb') as f:
    hexdata = f.read().hex()
    f.close()

bufferdata = hexdata
bufferlength = len(hexdata)

state = int(2)
temp = int(0)

while (True):
    while (bufferlength > 0):
        device_identifier = bufferdata[0:2]
        timestamp = int(bufferdata[2:10], 16)
        match device_identifier:
            case "00":
                temp = int(bufferdata[10:18], 16)
                err = int(bufferdata[18:20], 16)
                sensor_packet = TempSensorDatapacket(device_identifier, timestamp, err, temp)
                bufferdata = bufferdata[20:]
                log_output(sensor_packet)

            case "01":
                binary_state = int(bufferdata[10:12], 16)
                err = int(bufferdata[12:14], 16)
                sensor_packet = BinarySensorDatapacket(device_identifier, timestamp, err, binary_state)
                bufferdata = bufferdata[14:]
                log_output(sensor_packet)

        bufferlength = len(bufferdata)

    if not continuous_mode:
        break
