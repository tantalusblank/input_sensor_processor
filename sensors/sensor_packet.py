class SensorPacket:

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