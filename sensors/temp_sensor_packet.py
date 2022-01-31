from config import temp_limit_lower, temp_limit_upper
from sensors.sensor_packet import SensorPacket


class TempSensorPacket(SensorPacket):
    def __init__(self, extracted_packet_data):
        super().__init__(extracted_packet_data)
        self.temp_mil_deg = extracted_packet_data["sensor_val"]

    def __repr__(self):
        return "Packet Type: {}, " \
               "Millisec: {}, " \
               "Sec: {}, " \
               "Error Val: {}, " \
               "Error Calc: {}, " \
               "Error: {}, " \
               "Millideg: {}, " \
               "Degrees: {}".format(
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