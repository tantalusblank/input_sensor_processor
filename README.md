# Input Sensor Processor

A Python script to read hex packet data and output state changes to the command line. The data can be read from a file, but is set up with a buffer that can be filled from a continuous source.

A new packet type can be added by adding an entry with byte sizes at the beginning of the code. If necessary, these can be added to one of the sensor types, or a new sensor type can be added as a case.

Running the script with input data generates a log file in the specified folder.
