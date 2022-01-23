from datetime import datetime

# ***Script Options***

# Sets whether the log file clears each time the script runs:
clear_logs_on_run = True

# Sets whether the script continues to run after loading the input file into the buffer:
continuous_mode = False

# Import file (leave blank to skip import):
sensor_data_file = 'test/device_data.bin'

# Input sensors:
# Add another list inside sensor_devices to include another sensor
# Format is [Packet Type, Field Size 1, Field Size 2, Field Size 3, Field Size 4]
sensor_devices = [["00", 1, 4, 4, 1],
                  ["01", 1, 4, 1, 1]]

temp_limit_lower = 40
temp_limit_upper = 70


class SensorDataPacket:

    num_of_packets = 0

    def __init__(self, extracted_packet_data):
        self.packet_type = extracted_packet_data["packet_type"]
        self.timestamp_mil_sec = extracted_packet_data["timestamp"]
        self.sensor_val = extracted_packet_data["sensor_val"]
        self.error = extracted_packet_data["error"]

        SensorDataPacket.num_of_packets += 1

    def timestamp_sec(self):
        """Convert milliseconds to seconds"""
        if self.timestamp_mil_sec > 0:
            return int(self.timestamp_mil_sec / 1000)
        else:
            return self.timestamp_mil_sec

    def detect_error(self):
        """Check the error byte and return an error as True"""
        if self.error >= 256:
            return True
        else:
            return False


class TempSensorDataPacket(SensorDataPacket):
    def __init__(self, extracted_packet_data):
        super().__init__(extracted_packet_data)
        self.temp_mil_deg = extracted_packet_data["sensor_val"]

    def __repr__(self):
        return "{}, {}, {}, {}, {}".format(
            self.packet_type,
            self.timestamp_mil_sec,
            self.timestamp_sec(),
            self.error,
            self.temp_mil_deg)

    def temp_deg(self):
        """Convert milli-degrees Celsius to degrees Celsius"""
        if self.temp_mil_deg > 0:
            return int(self.temp_mil_deg / 1000)
        else:
            return self.temp_mil_deg

    def temp_in_range(self):
        """Determine whether the current temperature is within the safe operating range"""
        if self.temp_deg() > temp_limit_lower:
            if self.temp_deg() < temp_limit_upper:
                return "SAFE"
            else:
                return "UNSAFE"
        else:
            return "UNSAFE"


class BinarySensorDataPacket(SensorDataPacket):
    def __init__(self, extracted_packet_data):
        super().__init__(extracted_packet_data)

        self.binary_state = extracted_packet_data["sensor_val"]
        log_output(self)

    def __repr__(self):
        return "{}, {}, {}, {}, {}".format(
            self.packet_type,
            self.timestamp_mil_sec,
            self.timestamp_sec(),
            self.error,
            self.binary_state)

    def drawer_status(self):
        match self.binary_state:
            case 0:
                return "OPEN"
            case 1:
                return "CLOSED"
            case _:
                return "INVALID STATE"


def determine_sensor(sensor_devices, bufferdata):
    """Check the first byte in the packet to determine the sensor"""
    packet_identifier = bufferdata[:2]
    for i in sensor_devices:
        if packet_identifier in i:
            return sensor_devices[sensor_devices.index(i)]

def extract_packet_data(packet_template, bufferdata):
    """Extract sensor data from the buffer using the provided byte template"""
    pos1 = int(packet_template[1]) * 2
    pos2 = pos1 + int(packet_template[2]) * 2
    pos3 = pos2 + int(packet_template[3]) * 2
    pos4 = pos3 + int(packet_template[4]) * 2

    d1 = bufferdata[:pos1]
    d2 = int(bufferdata[pos1:pos2], 16)
    d3 = int(bufferdata[pos2:pos3], 16)
    d4 = int(bufferdata[pos3:pos4], 16)

    trim_length = 2*(packet_template[1] + packet_template[2] + packet_template[3] + packet_template[4])
    return {"trim_length": trim_length,
            "packet_type": d1,
            "timestamp": d2,
            "sensor_val": d3,
            "error": d4}

def log_output(sensor_packet):
    """Appends packet data to the log file"""
    with open('test/logs.txt', 'a') as logfile:
        logfile.writelines(str(datetime.now()) + ', ' + str(sensor_packet) + '\n')


# Open the file and read binary contents into a variable

# SETUP

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

safe_temp_last = ""

# LOOP

while (True):
    while (bufferlength > 0):

        # Check the first byte of the packet to determine the correct packet template
        packet_template = determine_sensor(sensor_devices, bufferdata)

        # Apply the packet template from the start of the buffer and store the data
        extracted_packet_data = extract_packet_data(packet_template, bufferdata)

        # Trim the packet length from the start of the buffer data
        bufferdata = bufferdata[extracted_packet_data["trim_length"]:]
        bufferlength = len(bufferdata)

        # Create objects of the relevant class if one is available
        sensor_packet = SensorDataPacket(extracted_packet_data)

        if sensor_packet.error == True:
            print("ERROR:Bad Packet, Time:", sensor_packet.timestamp_mil_sec, " Error:", sensor_packet.error)
            log_output(sensor_packet)

        match extracted_packet_data["packet_type"]:
            case "00":
                sensor_packet = TempSensorDataPacket(extracted_packet_data)
                safe_temp = sensor_packet.temp_in_range()
                if safe_temp != safe_temp_last:
                    print("T:", sensor_packet.timestamp_sec(), ":", safe_temp)
                safe_temp_last = safe_temp

            case "01":
                sensor_packet = BinarySensorDataPacket(extracted_packet_data)
                timestamp = sensor_packet.timestamp_sec()
                print("D:", sensor_packet.timestamp_sec(), ":", sensor_packet.drawer_status())
            # case _:
            #     sensor_packet = SensorDataPacket(extracted_packet_data)

        # Append the resulting packet data to the log file
        log_output(sensor_packet)

    if not continuous_mode:
        break
