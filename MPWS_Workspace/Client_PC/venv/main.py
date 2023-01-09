from WifiClientPC import ClientPC
from WeatherStationGUI import WSGUI
from ClientData import ClientData

def main():
    # For saving measurement and protocol data
    client_data = ClientData()

    # Client wifi program
    client_pc = ClientPC()
    # Connect to the Fipy Serwer
    (meas_socket, proto_choice_socket) = client_pc.connect_to_server()
    # Start reading measurement from FiPy thread
    client_pc.start_meas_thread(client_data)

    # Create gui, protocol choice socket from client_pc as argument
    mywin = WSGUI(client_data, proto_choice_socket)


if __name__ == '__main__':
    main()


