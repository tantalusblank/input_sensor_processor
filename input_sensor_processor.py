from datetime import datetime

# ***Script Options***

# Sets whether the log file clears each time the script runs:
clear_logs_on_run = True

# Sets whether the script continues to run after loading the input file into the buffer:
continuous_mode = False

# Import file (leave blank to skip import):
sensor_data_file = 'test/device_data.bin'

# Log file:
log_file_path = 'test/logs.txt'

# Input sensors:
# Add another list inside packet_templates to include another sensor
# Format is [Packet Type, Field Size 1, Field Size 2, Field Size 3, Field Size 4]
packet_templates = [["00", 1, 4, 4, 1],
                    ["01", 1, 4, 1, 1]]

temp_limit_lower = 40
temp_limit_upper = 70


class SensorDataPacket:

    def __init__(self, extracted_packet_data):
        self.packet_type = extracted_packet_data["packet_type"]
        self.timestamp_mil_sec = extracted_packet_data["timestamp"]
        self.sensor_val = extracted_packet_data["sensor_val"]
        self.error = extracted_packet_data["error"]
        self.error_calc = extracted_packet_data["error_calc"]

    def from_milli(self, unit_to_convert):
        """Convert from milli to standard units"""
        if unit_to_convert > 0:
            return int(unit_to_convert / 1000)
        else:
            return unit_to_convert

    def detect_error(self):
        """Check the data against the error byte"""
        if self.error == self.error_calc:
            return False
        else:
            return True


class TempSensorDataPacket(SensorDataPacket):
    def __init__(self, extracted_packet_data):
        super().__init__(extracted_packet_data)
        self.temp_mil_deg = extracted_packet_data["sensor_val"]

    def __repr__(self):
        return "{}, {}, {}, {}, {}, {}, {}, {}".format(
            self.packet_type,
            self.timestamp_mil_sec,
            self.from_milli(self.timestamp_mil_sec),
            self.error,
            self.error_calc,
            self.detect_error(),
            self.temp_mil_deg,
            self.from_milli(self.temp_mil_deg))

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

    def __repr__(self):
        return "{}, {}, {}, {}, {}, {}, {}".format(
            self.packet_type,
            self.timestamp_mil_sec,
            self.from_milli(self.timestamp_mil_sec),
            self.error,
            self.error_calc,
            self.detect_error(),
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
    """Check the first byte in the packet to determine the sensor template"""
    packet_identifier = bufferdata[:2]
    for i in sensor_devices:
        if packet_identifier in i:
            return sensor_devices[sensor_devices.index(i)]


def extract_packet_data(packet_template, bufferdata):
    """Extract sensor data from the buffer using the provided byte template"""
    pos1 = packet_template[1] * 2
    pos2 = pos1 + packet_template[2] * 2
    pos3 = pos2 + packet_template[3] * 2
    pos4 = pos3 + packet_template[4] * 2

    d1 = bufferdata[:pos1]
    d2 = int(bufferdata[pos1:pos2], 16)
    d3 = int(bufferdata[pos2:pos3], 16)
    d4 = int(bufferdata[pos3:pos4], 16)

    trim_length = 2*(packet_template[1] +
                     packet_template[2] +
                     packet_template[3] +
                     packet_template[4])

    char_to_count = list(range(0, pos3, 2))
    error_sum = 0
    for i in char_to_count:
        error_sum += int(bufferdata[i:i+2], 16)
    error_calc = error_sum % 256

    return {"trim_length": trim_length,
            "packet_type": d1,
            "timestamp": d2,
            "sensor_val": d3,
            "error": d4,
            "error_calc": error_calc}


def log_output(sensor_packet):
    """Appends packet data to the log file"""
    with open(log_file_path, 'a') as logfile:
        logfile.writelines(
            str(datetime.now()) +
            ', ' +
            str(sensor_packet) +
            '\n')


def clear_log():
    """Clears the log if configured to"""
    if clear_logs_on_run == True:
        with open(log_file_path, 'w') as logfile:
            logfile.write('')


def read_from_file(sensor_data_file):
    """Reads data from a binary file and returns a string in hex"""
    with open(sensor_data_file, 'rb') as f:
        hex_data = f.read().hex()
        return hex_data


# SETUP
clear_log()

bufferdata = ""
bufferdata += read_from_file(sensor_data_file)

bufferlength = len(bufferdata)

safe_temp_last = ""

# LOOP
while (True):
    while (bufferlength > 0):

        # Check the first byte of the packet to determine the correct packet template
        packet_template = determine_sensor(packet_templates, bufferdata)

        # Apply the packet template from the start of the buffer and store the data
        extracted_packet_data = extract_packet_data(packet_template, bufferdata)

        # Trim the packet length from the start of the buffer data
        bufferdata = bufferdata[extracted_packet_data["trim_length"]:]
        bufferlength = len(bufferdata)

        # Create a packet object with the subclass to match the packet type
        match packet_template[0]:
            case "00":
                sensor_packet = TempSensorDataPacket(extracted_packet_data)
                safe_temp = sensor_packet.temp_in_range()
                if safe_temp != safe_temp_last:
                    print("T:",
                          sensor_packet.from_milli(sensor_packet.timestamp_mil_sec),
                          ":",
                          safe_temp)
                safe_temp_last = safe_temp

            case "01":
                sensor_packet = BinarySensorDataPacket(extracted_packet_data)
                print("D:",
                      sensor_packet.from_milli(sensor_packet.timestamp_mil_sec),
                      ":",
                      sensor_packet.drawer_status())

            case _:
                sensor_packet = SensorDataPacket(extracted_packet_data)

        log_output(sensor_packet)

    if not continuous_mode:
        break
