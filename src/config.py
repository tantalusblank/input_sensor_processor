temp_limit_lower = 40
temp_limit_upper = 70
log_file_path = './logs.txt'
test_file_path = '../test/device_data.bin'

# Format is [Packet Type, Field Size 1, Field Size 2, Field Size 3, Field Size 4]
packet_templates = [["00", 1, 4, 4, 1],
                    ["01", 1, 4, 1, 1]]

clear_logs_on_run = True

# Sets whether the script continues to run after loading the input file into the buffer:
continuous_mode = True

