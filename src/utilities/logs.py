from datetime import datetime
from config import log_file_path, clear_logs_on_run


def log_output(sensor_packet):
    """Appends packet data to the log file"""
    with open(log_file_path, 'a') as logfile:
        logfile.writelines(
            "System timestamp: " +
            str(datetime.now()) +
            ', ' +
            str(sensor_packet) +
            '\n')


def clear_log():
    """Clears the log if configured to"""
    if clear_logs_on_run == True:
        with open(log_file_path, 'w') as logfile:
            logfile.write('')