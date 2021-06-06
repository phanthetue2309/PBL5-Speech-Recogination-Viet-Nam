import serial


def dithang():
    bluetooth.write(str.encode("A"))
    input_data = bluetooth.readline()
    print(input_data.decode())


def dunglai():
    bluetooth.write(str.encode("B"))
    input_data = bluetooth.readline()
    print(input_data.decode())


def quaytrai():
    bluetooth.write(str.encode("C"))
    input_data = bluetooth.readline()
    print(input_data.decode())


def quayphai():
    bluetooth.write(str.encode("D"))
    input_data = bluetooth.readline()
    print(input_data.decode())


def sangtrai():
    bluetooth.write(str.encode("E"))
    input_data = bluetooth.readline()
    print(input_data.decode())


def sangphai():
    bluetooth.write(str.encode("F"))
    input_data = bluetooth.readline()
    print(input_data.decode())


port = 'COM7'  # windows it will probably be a COM port.
# Start communications with the bluetooth unit
bluetooth = serial.Serial(port, 9600)
print("Connected to Divice")
bluetooth.flushInput()  # This gives the bluetooth a little kick

while(1):
    print("nhap value")
    value = input()
    if (value == "1"):
        dithang()
    if (value == "2"):
        dunglai()
    if (value == "3"):
        quaytrai()
    if (value == "4"):
        quayphai()
    if (value == "5"):
        sangtrai()
    if (value == "6"):
        sangphai()
    if (value == "7"):
        break

bluetooth.close()
print("Done")
