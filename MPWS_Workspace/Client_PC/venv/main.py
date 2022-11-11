import WeatherStationGUI as wsg
import tkinter as tk
import threading
import time
import socket
import struct
from Client_PC import PC_CLIENT


def main():
    # Client wifi program
    client_pc = PC_CLIENT()

    # Create gui
    window = tk.Tk()
    mywin = wsg.WeatherStationGUI(window)

    # Start GUI
    window.mainloop()


if __name__ == '__main__':
    main()


