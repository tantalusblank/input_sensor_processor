def read_from_file(sensor_data_file):
    """Reads data from a binary file and returns a string in hex"""
    with open(sensor_data_file, 'rb') as f:
        hex_data = f.read().hex()
        return hex_data