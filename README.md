# Input Sensor Processor

A Python script to read hex packet data and output state changes to the command line. The data can be read from a file, but is set up with a buffer that can be filled from a continuous source.

A new packet type can be added by adding an entry with byte sizes at the beginning of the code. If necessary, these can be added to one of the sensor types, or a new sensor type can be added as a case.

Running the script with input data generates a log file in the specified folder.

## Instructions For Use
Run **input_sensor_processor.exe** from the command line with one positional argument - the file path of the data to be read

*e.g. input_sensor_processor.exe device_data.bin*

The configuration can be modified in config.py. To create a new executable with the new configuration, run compile_to_exe.py
