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
	# TODO
    return 0

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