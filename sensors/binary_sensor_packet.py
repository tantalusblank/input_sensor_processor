from sensors.sensor_packet import SensorPacket


class BinarySensorPacket(SensorPacket):
    def __init__(self, extracted_packet_data):
        super().__init__(extracted_packet_data)
        self.binary_state = extracted_packet_data["sensor_val"]

    def __repr__(self):
        return "Packet Type: {}, " \
               "Millisec: {}, " \
               "Sec: {}, " \
               "Error Val: {}, " \
               "Error Calc: {}, " \
               "Error: {}, " \
               "State: {}".format(
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