import argparse

from src.inputs.from_file import read_from_file
from src.sensors.binary_sensor_packet import BinarySensorPacket
from src.sensors.sensor_packet import SensorPacket
from src.sensors.temp_sensor_packet import TempSensorPacket
from src.utilities.logs import log_output, clear_log
from src.config import packet_templates, continuous_mode


def determine_sensor(packet_templates, bufferdata):
    """Check the first byte in the packet to determine the sensor template"""
    packet_identifier = bufferdata[:2]
    for i in packet_templates:
        if packet_identifier in i:
            return packet_templates[packet_templates.index(i)]


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

    trim_length = 2 * (packet_template[1] +
                       packet_template[2] +
                       packet_template[3] +
                       packet_template[4])

    char_to_count = list(range(0, pos3, 2))
    error_sum = 0
    for i in char_to_count:
        error_sum += int(bufferdata[i:i + 2], 16)
    error_calc = error_sum % 256

    return {"trim_length": trim_length,
            "packet_type": d1,
            "timestamp": d2,
            "sensor_val": d3,
            "error": d4,
            "error_calc": error_calc}


# SETUP
parser = argparse.ArgumentParser(description='Specify Input File', exit_on_error=False)
parser.add_argument('file_path', type=str, nargs='?', help='File Path')
args = parser.parse_args()

if __name__ == '__main__':

    clear_log()

    bufferdata = ""
    safe_temp_last = ""

    try:
        bufferdata += read_from_file(args.file_path)
    except:
        print("No valid data file selected")

    bufferlength = len(bufferdata)

    # LOOP
    while True:
        while bufferlength > 0:

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
                    sensor_packet = TempSensorPacket(extracted_packet_data)
                    safe_temp = sensor_packet.temp_in_range()
                    if safe_temp != safe_temp_last:
                        print("T:",
                              sensor_packet.from_milli(sensor_packet.timestamp_mil_sec),
                              ":",
                              safe_temp)
                    safe_temp_last = safe_temp

                case "01":
                    sensor_packet = BinarySensorPacket(extracted_packet_data)
                    print("D:",
                          sensor_packet.from_milli(sensor_packet.timestamp_mil_sec),
                          ":",
                          sensor_packet.drawer_status())

                case _:
                    sensor_packet = SensorPacket(extracted_packet_data)

            if sensor_packet.detect_error():
                print("ERROR: Bad Packet")

            log_output(sensor_packet)

        if not continuous_mode:
            break
