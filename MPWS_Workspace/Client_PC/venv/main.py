import WeatherStationGUI as wsg
import tkinter as tk
import threading
import time
import socket
import struct
from Client_PC import PC_CLIENT
import WeatherStationGraphs as wsgraph


def main():
    # Client wifi program
    client_pc = PC_CLIENT()

    # Create gui
    mywin = wsg.WeatherStationGUI(client_pc)

    # Start GUI
    mywin.mainloop()


if __name__ == '__main__':
    main()


