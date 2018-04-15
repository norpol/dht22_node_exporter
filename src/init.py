#!/usr/bin/env python3
"""
A node_export text exporter script
for reading a serial console temp_humidity sensor
https://jeffknupp.com/blog/2014/02/04/starting-a-python-project-the-right-way/
"""
import sys
import argparse
import serial

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
            "input", nargs="?", default="-",
            metavar="SERIAL", type=argparse,
            help="path to the serial-device or testing file, default stdin '-'")
    parser.add_argument(
            "output", nargs="?", default="-",
            metavar="OUTPUT", type=argparse,
            help="script output, default stdout '-'")

    args = parser.parse_args()
    write_position_into_file(args.input, args.output)

def write_position_into_file(tty, output):
    """
    write a prometheus line into a file
    """
    with open(output,'w') as f:
        for line in combine_two_tuples(read_serial(tty)):
            f.truncate(0)
            f.seek(0)
            for items in line:
                output=' '.join(items)
                f.write(str(output) + '\n')
            f.flush()
        f.close()

def read_file(fname):
    """
    loop through file device
    """
    import time
    data = {}
    with open(fname) as f:
        for line in f.readlines():
            time.sleep(2)
            yield parse_line(line)

def read_serial(device):
    """
    loop through serial device
    """
    import serial
    with serial.Serial(device, 19200, timeout=1) as ser:
        line = ser.read()
        yield parse_line(line)

def parse_line(line):
    """
    parse a single line of my sensor output
    return a tuple of elements
    http://effbot.org/zone/simple-top-down-parsing.htm
    https://gist.github.com/liyu1981/2f29f8d031fa263be10e
    http://zderadicka.eu/writing-simple-parser-in-python/
    https://fdik.org/pyPEG/
    https://stackoverflow.com/questions/2945357/how-best-to-parse-a-simple-grammar
    """
    """
    TODO: Figure out how to use static typing
    read about mypy etc
    http://mypy-lang.org/
    https://docs.python.org/3/library/typing.html """

    line=line.strip()
    data=[]
    reset="Humidity %,     Temperature °C, Sensor-ID"
    types={
        "%": { "name": "relative_humidity_percent", "type": "float" },
        "C": { "name": "temperature_degree_celcius", "type": "float" },
        "i": { "name": "identifier", "type": "string"}
    }

    if line == reset:
        return([("sensor_reset", "True")])
    for field in line.split():
        try:
            name=types[field[-1]]['name']
            value=field[0:-1]
        except KeyError:
            name="failed_to_parse"
            value=field
        data.append((name, value))
    return(data)

def detect_serial_devices():
    """ detect correct serial devices and
    return tuple with devices
    https://stackoverflow.com/questions/24214643/python-to-automatically-select-serial-ports-for-arduino
    """
    pass

def return_node_exporter_data():
    """
    https://github.com/prometheus/node_exporter/blob/master/text_collector_examples/storcli.py
    https://www.robustperception.io/quick-sensor-metrics-with-the-textfile-collector/
    example
    """

def combine_two_tuples(data):
    """
    serial buffer memorizes last collected value on serial attach and then responses with reset message
    make sure we throw away data before sensor_reset
    """
    two=[]
    for i in data:
        two.append(i)
        if len(two) == 2:
            snd=two[1][0]
            if snd[0] == 'sensor_reset' and snd[1] == 'True':
                yield two.pop()
            else:
                yield two.pop()

"""
test
http://docs.python-guide.org/en/latest/writing/tests/
https://docs.python.org/3.6/library/unittest.html
http://www.science.smith.edu/dftwiki/index.php/PySerial_Simulator
"""

if __name__ == "__main__":
    sys.exit(main())
