import tkinter as tk
from tkinter import messagebox
import sys
import socket
import threading


class WeatherStationGUI:
    def __init__(self, win):
        self.proto = 'none'
        self.protobuff = 'none'
        self.window = win
        self.window.geometry("490x250+550+300")
        self.window.title("Weather station controller")
        self.window.resizable(0, 0)
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        # Create frame with label
        self.frame_messg = tk.Frame(self.window, relief=tk.RAISED, bd=2)
        self.label_messg = tk.Label(self.frame_messg, text="Please choose protocol:", font=12, width=43, height=2)
        self.label_messg.pack(padx=5, pady=5)

        # Create frame with buttons
        self.frame_buttons = tk.Frame(self.window, relief=tk.RAISED, bd=2)
        self.button_wifi = tk.Button(self.frame_buttons, text="WiFi", command=self.wifi_choice, font=12)
        self.button_ble = tk.Button(self.frame_buttons, text="BLE", command=self.ble_choice, font=12)
        self.button_sigfox = tk.Button(self.frame_buttons, text="Sigfox", command=self.sigfox_choice, font=12)
        self.button_lte = tk.Button(self.frame_buttons, text="LTE-M", command=self.lte_choice, font=12)
        self.button_wifi.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.button_ble.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.button_sigfox.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        self.button_lte.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")

        # Create frame with label
        self.frame_proto_choice = tk.Frame(self.window, relief=tk.RAISED, bd=2)
        self.label_proto_choice = tk.Label(self.frame_proto_choice, text=f"Choice: {self.proto}", font=12, width=43, height=2)
        self.label_proto_choice.pack(padx=5, pady=5)

        # Create frame with label for interacting with user
        self.frame_inter = tk.Frame(self.window, relief=tk.RAISED, bd=2)
        self.label_inter = tk.Label(self.frame_inter, text=f"", font=12, width=43, height=2, fg='red')
        self.label_inter.pack(padx=5, pady=5)

        # Set our frames on window
        self.frame_messg.grid(row=0, column=0, sticky="nsew")
        self.frame_buttons.grid(row=1, column=0)
        self.frame_proto_choice.grid(row=2, column=0, sticky="nsew")
        self.frame_inter.grid(row=3, column=0, sticky="nsew")

        # Create a proto choice socket
        self.client_protocol_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server - protocol choice socket
        self.SERVER_ADDRESS = '192.168.4.1'
        self.SERVER_PORT = 50000
        self.client_protocol_socket.connect(socket.getaddrinfo(self.SERVER_ADDRESS, self.SERVER_PORT)[0][-1])
        print('Connected to the server - protocol choice socket')

        # Create thread for protocol choice
        self.proto_thread = threading.Thread(target=self.proto_choice_thread, args=(self.client_protocol_socket,))
        self.proto_thread.daemon = True  # Daemon threads are those threads which are killed when the main program exits.
        self.proto_thread.start()


    def proto_choice_thread(self, proto_socket):
        while True:
            if self.proto != self.protobuff:
                if self.proto == 'WiFi':
                    proto_socket.send(b'WiFi')
                    self.protobuff = 'WiFi'
                elif self.proto == 'BLE':
                    proto_socket.send(b'BLE')
                    self.protobuff = 'BLE'
                elif self.proto == 'Sigfox':
                    proto_socket.send(b'Sigfox')
                    self.protobuff = 'Sigfox'
                elif self.proto == 'LTE-M':
                    proto_socket.send(b'LTE-M')
                    self.protobuff = 'LTE-M'
        proto_socket.close()


    def wifi_choice(self):
        self.label_inter["text"] = ""
        self.proto = 'WiFi'
        if self.proto != self.protobuff:
            self.label_proto_choice["text"] = f"Choice: {self.proto}"
            print('Button: WiFi')
        else:
            self.label_inter["text"] = f"{self.proto} is actually choosen"


    def ble_choice(self):
        self.label_inter["text"] = ""
        self.proto = 'BLE'
        if self.proto != self.protobuff:
            self.label_proto_choice["text"] = f"Choice: {self.proto}"
            print('Button: BLE')
        else:
            self.label_inter["text"] = f"{self.proto} is actually choosen"


    def sigfox_choice(self):
        self.label_inter["text"] = ""
        self.proto = 'Sigfox'
        if self.proto != self.protobuff:
            self.label_proto_choice["text"] = f"Choice: {self.proto}"
            print('Button: Sigfox')
        else:
            self.label_inter["text"] = f"{self.proto} is actually choosen"


    def lte_choice(self):
        self.label_inter["text"] = ""
        self.proto = 'LTE-M'
        if self.proto != self.protobuff:
            self.label_proto_choice["text"] = f"Choice: {self.proto}"
            print('Button: LTE')
        else:
            self.label_inter["text"] = f"{self.proto} is actually choosen"


    def close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.window.destroy()