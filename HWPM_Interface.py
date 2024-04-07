"""Hardware Password Manager Interface
Interface to interact with the HWPM.

Adds credentials, loads them on the HWPM and retrieves them from there.

Usage: 
    HWPM_Interface.py [ --check-connection ] [--port PORT]
    HWPM_Interface.py [ --add-credentials ] [--out-file OUT_FILE]
    HWPM_Interface.py [ --transfer ] [--port PORT] [--out-file OUT_FILE]
    HWPM_Interface.py [ --retrieve ] [--port PORT]  [--out-file OUT_FILE]
    HWPM_Interface.py [ --import ] [--in-file IN_FILE]  [--out-file OUT_FILE]

Options:
    --check-connection          Checks for a connection with a HWPM on the given port. (See also --port)
    --add-credentials           Adds a new set of credentials
    --transfer                  Transfers all saved credentials to the HWPM
    --retrieve                  Retreives all credentials from the HWPM
    --import                    Imports a .csv of credentials from a browser

    --port                      Specifies the port to which the HWPM is connected. If none is given, 
                                it defaults to /dev/ttyACM0.
    --in-file                   Specifies the file from which data is read. If none is given, it 
                                defaults to credentials.csv.
    --out-file                  Specifies the file to which data is written. If none is given, it 
                                defaults to HWPM.csv.
"""

import serial
import os.path
import time

from docopt import docopt

import Interface_auxillary as aux

port = '/dev/ttyACM0'
baudrate = 9600
in_file = "credentials.csv"
out_file = "HWPM.csv"

code = 0

def main(arguments):
    # Checks for the three optional parameters:
    if arguments['--port']:
        port = arguments['--port']
    if arguments['--in-file']:
        in_file = arguments['--in-file']
    if arguments['--out-file']:
        out_file = arguments['--out-file']

    # Check if anything is connecting. Fot this it pings the port
    if arguments['--check-connection']:
        try:
            arduino = aux.getConnection(port, baudrate)
            answer = aux.write(arduino, "ping")
        except serial.serialutil.SerialException:
            print("No connection found")
            exit(0)
            
        if (answer == "pong"):
            print("Arduino is connected!")
        else:
            print("A connection was found but the answer was unexpected. Please check that everything is well connected.")
        exit(0)

    # Adds new credentials
    if arguments['--add-credentials']:
        code = aux.getCode()
        aux.addCredentials(out_file, code)
        exit(0)

    # Transfers the credentials to the stick
    if arguments['--transfer']:
        aux.transferToStick(out_file, port, baudrate)
        exit(0)

    # Retrieve credentials from the stick
    if arguments['--retrieve']:
        aux.retrieveData(out_file, port, baudrate)
        exit(0)

    # Imports credentials from a .csv
    if arguments['--import']:
        code = aux.getCode()
        aux.importData(in_file, out_file, code)
        exit(0)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='HWPM-Interface Version Alpha-0.1')
    main(arguments)