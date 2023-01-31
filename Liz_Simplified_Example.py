import serial


def send_command(command, serial):
    serial.write(command.encode())
    serial.write(b'\r')

def get_response(serial):
    response = serial.readline()
    response = response.decode('ascii')
    return response

if __name__ == '__main__':
    # Open serial port
    Com_port = 'COM3'
    ser = serial.Serial(Com_port,baud= 9600, timeout= 1)

    #Commands
    #On/off
    Turn_on = "OUTPUT ON"
    Turn_off = "OUTPUT OFF"
    #maeasure
    MeasureCurrent = "MEAS:CURR:DC?"
    MeasureVoltage = "MEAS:VOLT:DC?"
    #Set
    SetCurrent = "CURR 0.1"
    SetVoltage = "VOLT 5"

    #Send command
    send_command(SetCurrent, ser)
    send_command(SetVoltage, ser)
    send_command(Turn_on, ser)

    #Get response
    response = get_response(ser)
    print(response)

    #measure
    send_command(MeasureCurrent, ser)
    response = get_response(ser)
    print(response)

    send_command(MeasureVoltage, ser)
    response = get_response(ser)
    print(response)

    #Turn off
    send_command(Turn_off, ser)

    #Close serial port
    ser.close()