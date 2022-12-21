from Client_PC import PC_CLIENT
from WeatherStationGUI import WSGUI


def main():
    # Client wifi program
    client_pc = PC_CLIENT()

    # Create gui
    mywin = WSGUI(client_pc)


if __name__ == '__main__':
    main()


