import pytest
from src.inputs.from_file import read_from_file
from src.config import test_file_path, packet_templates
from src.input_sensor_processor import extract_packet_data
from src.sensors.sensor_packet import SensorPacket

read_file_data = read_from_file(test_file_path)

packet_input_1 = [0, 5, 4000, 180]
packet_input_1_check = {'trim_length': 20,
                        'packet_type': '00',
                        'timestamp': 5,
                        'sensor_val': 4000,
                        'error': 180,
                        'error_calc': 180}

packet_input_2 = [1, 200, 1, 100]
packet_input_2_check = {'error': 100,
                        'error_calc': 202,
                        'packet_type': '01',
                        'sensor_val': 1,
                        'timestamp': 200,
                        'trim_length': 14}


def select_template(packet_templates, device):
    """Selects the correct template for an example packet"""
    device_str = str.zfill(str(device), 2)
    for i in packet_templates:
        if device_str in i:
            return packet_templates[packet_templates.index(i)]


def convert_to_hex_string(template_val, width):
    """Converts an integer to a hex string of a specific length"""
    string_short = str(hex(template_val)[2:])
    string_correct_length = string_short.zfill(width)
    return string_correct_length


def packet_example_builder(example_packet):
    """Builds an example packet string"""
    packet_template = select_template(packet_templates, example_packet[0])
    packet_string = (
        convert_to_hex_string(example_packet[0], packet_template[1]*2) +
        convert_to_hex_string(example_packet[1], packet_template[2]*2) +
        convert_to_hex_string(example_packet[2], packet_template[3]*2) +
        convert_to_hex_string(example_packet[3], packet_template[4]*2)
    )
    return packet_string


def test_read_from_file_is_string():
    # print(packet_example_builder(packet_input_1))
    # print(packet_example_builder(packet_input_2))
    assert type(read_file_data) is str


def test_read_from_file_is_correct_length():
    assert len(read_file_data) >= 4


def compare_expected_dictionary(packet_input, packet_input_check):
    packet_template = select_template(packet_templates, packet_input[0])
    example_packet = extract_packet_data(packet_template, packet_example_builder(packet_input))
    assert example_packet == packet_input_check


def test_extract_packet_data_temp():
    compare_expected_dictionary(packet_input_1, packet_input_1_check)


def test_extract_packet_data_binary():
    compare_expected_dictionary(packet_input_2, packet_input_2_check)


def test_detect_error_false():
    packet_obj = SensorPacket(packet_input_1_check)
    assert packet_obj.detect_error() is False


def test_detect_error_true():
    packet_obj = SensorPacket(packet_input_2_check)
    assert packet_obj.detect_error() is True
