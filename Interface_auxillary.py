import serial
import os.path
import time

key = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?!\"§$%&/()=^°{[]}\+*~#'-_.:,;<>|"

def addCredentials(filename, code):
	if (not os.path.isfile(filename)):
		print("No file found named " + filename)
		exit(0)
		
	name = input("Please enter the name of the new set of credentials:")
	username = input("Please enter the username:")
	password = input("Please enter the password:")
	password = encrypt(password, code, key)

	file = open(filename, 'a')
	cred = name + "\t" + username + "\t" + password + "\n"
	file.write(cred)
	file.close()
	
	print("Added the new set of credentials!")
 
def transferToStick(filename, port, baudrate):
	# TODO: wipe before
	if (not os.path.isfile(filename)):
		print("No file found named " + filename)
		exit(0)
		
	# Check for connection and correct mode
	try:
		arduino = getConnection(port, baudrate)
		answer = write(arduino, "mode")
	except serial.serialutil.SerialException:
		print("No connection found")
		exit(0)
        
	if (not answer == "saving"):
		print("A connection was found but the answer was unexpected. Please check that everything is well connected and the HWPM is in Saving mode.")
		exit(0)
		
	file = open(filename, 'r')
	temp = file.read().splitlines()
	
	for line in temp:
		print(line)
		answer = write(arduino, line)
		if ("I received: " + line == answer):
			print("Successfully transmitted " + line)
		else:
			print("Did not send data properly!")
	file.close()
 
def retrieveData(filename, port, baudrate):
	file = open(filename, 'w')
	
	# Check for connection and correct mode
	try:
		arduino = getConnection(port, baudrate)
		answer = write(arduino, "mode")
	except serial.serialutil.SerialException:
		print("No connection found")
		exit(0)
        
	if (not answer == "saving"):
		print("A connection was found but the answer was unexpected. Please check that everything is well connected and the HWPM is in Saving mode.")
		exit(0)

	write("sendAll")
	data = arduinoRead()
	file = open(filename, 'a')
	print(data) # save to file instead
	file.close()
	# TODO
 
def importData(in_file, out_file, code):
    """
    Imports data from a CSV file (e.g., browser export) and writes it in HWPM format (tab-separated, password encrypted) to out_file.
    The CSV file should contain the columns: Name, Username, Password (German column names are also supported).
    """
    import csv
    # Check if the input file exists
    if not os.path.isfile(in_file):
        print(f"Input file {in_file} not found.")
        return 1
    try:
        with open(in_file, 'r', encoding='utf-8') as csvfile:
            # Try different delimiters (comma and semicolon)
            try:
                reader = csv.reader(csvfile, delimiter=',')
                rows = list(reader)
                if len(rows) == 0 or len(rows[0]) < 2:
                    raise Exception()
            except:
                csvfile.seek(0)
                reader = csv.reader(csvfile, delimiter=';')
                rows = list(reader)
        header = rows[0]
        # Try to find column names, also supporting German names
        name_idx = None
        user_idx = None
        pass_idx = None
        for i, h in enumerate(header):
            h_lower = h.strip().lower()
            # Allow 'benutzername' and 'passwort' as column names
            if 'name' in h_lower and 'benutzer' not in h_lower:
                name_idx = i
            elif 'user' in h_lower or 'benutzer' in h_lower:
                user_idx = i
            elif 'pass' in h_lower or 'wort' in h_lower:
                pass_idx = i
        # Check if all required columns were found
        if None in (name_idx, user_idx, pass_idx):
            print("CSV header must contain Name, Username and Password (German names are also supported).")
            print(f"Header found: {header}")
            return 2
        with open(out_file, 'a', encoding='utf-8') as outfile:
            for row in rows[1:]:
                # Skip incomplete rows
                if len(row) <= max(name_idx, user_idx, pass_idx):
                    continue
                name = row[name_idx].strip()
                username = row[user_idx].strip()
                password = row[pass_idx].strip()
                # Encrypt the password using the existing encrypt function
                password_enc = encrypt(password, code, key)
                # Write the data in HWPM format (tab-separated) to the output file
                outfile.write(f"{name}\t{username}\t{password_enc}\n")
        print(f"Import finished. {len(rows)-1} entries processed.")
        return 0
    except Exception as e:
        # Error handling with exception output
        print(f"Error during import: {e}")
        return 3

def getConnection(port, baudrate):
	return serial.Serial(port=port, baudrate=baudrate)
	
def getCode():
	code_string = input("Please enter the Code for the encryption:")
	code = []
	for c in code_string:
		code.append(ord(c) - ord('0'))
	return input("Please enter the Code for the encryption:")

def encrypt(string,code,key):
	out = ""
	j = 0
	for c in string:
		i = key.index(c)
		out += key[(i - code[j]) % len(key)]
		j = (j + 1) % len(code)
	return out

def decrypt(string,code,key):
	out = ""
	j = 0
	for c in string:
		i = key.index(c)
		out += key[(i + code[j]) % len(key)]
		j = (j + 1) % len(code)
	return out

def write(arduino, string):
	arduino.write(bytes(string, 'utf-8'))
	data = arduinoRead().decode('utf-8')
	return data[:-2]
			
def arduinoRead(arduino):
	data = arduino.read()
	time.sleep(0.05)
	data_left = arduino.inWaiting()
	data += arduino.read(data_left)
	return data

def arduinoEquals(string, data):
	string = string + "\r\n"
	byte_data = string.encode("utf-8")
	return (data == byte_data)