import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import pyplot as plt, animation
from tkinter import messagebox
import numpy as np
import datetime as dt
import socket
import time
import threading



class WSGUI(tk.Tk):
    def __init__(self, client_pc):
        self.client_pc = client_pc
        self.proto = 'none'
        self.protobuff = 'none'
        self.xs = []
        self.ys1 = []
        self.ys2 = []
        self.ys3 = []
        self.ys4 = []

        super().__init__()
        self.wm_title('Weather station controller')
        self.state('zoomed')
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.fig = plt.Figure(dpi=100)
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)

        # Create animation graphs
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.update()

        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        # toolbar.grid(row=4, column=0)
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        # canvas.get_tk_widget().grid(row=4,column=0, sticky='n')

        anim = animation.FuncAnimation(self.fig, self.animate, interval=5000)

        # Create label
        self.label_messg = tk.Label(self, text="Please choose network:", font=12, width=43, height=2)
        self.label_messg.pack(side=tk.TOP, fill=tk.X)

        # Create frame with buttons
        self.frame_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)
        self.button_wifi = tk.Button(self.frame_buttons, text="WiFi", command=self.wifi_choice, font=12)
        self.button_ble = tk.Button(self.frame_buttons, text="BLE", command=self.ble_choice, font=12)
        self.button_lora = tk.Button(self.frame_buttons, text="LoRa", command=self.lora_choice, font=12)
        self.button_wifi.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        self.button_ble.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        self.button_lora.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')
        self.frame_buttons.pack()

        # Create label for print protocol choice
        self.label_proto_choice = tk.Label(self, text=f"Choice:{self.proto}", font=12, width=43, height=2)
        self.label_proto_choice.pack(side=tk.TOP, fill=tk.X)

        # Create frame with label for interacting with user
        self.label_inter = tk.Label(self, text=f"", font=12, width=43, height=2, fg='red')
        self.label_inter.pack(side=tk.TOP, fill=tk.X)

        # Create a proto choice socket
        self.client_protocol_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server - protocol choice socket
        self.SERVER_ADDRESS = '192.168.4.1'
        self.SERVER_PORT = 50000
        self.client_protocol_socket.connect(socket.getaddrinfo(self.SERVER_ADDRESS, self.SERVER_PORT)[0][-1])
        print('Connected to the server - protocol choice socket')

        self.mainloop()

    def animate(self, i):
        if self.client_pc.AM2320_HUMIDITY and self.client_pc.AM2320_TEMPERATURE and self.client_pc.LPS25HB_PRESSURE and self.client_pc.LPS25HB_TEMPERATURE != 0:  # wait for measurement after start program
            # Add x and y to lists
            self.xs.append(dt.datetime.now().strftime('%H:%M:%S'))
            self.ys1.append(self.client_pc.AM2320_TEMPERATURE)
            self.ys2.append(self.client_pc.AM2320_HUMIDITY)
            self.ys3.append(self.client_pc.LPS25HB_TEMPERATURE)
            self.ys4.append(self.client_pc.LPS25HB_PRESSURE)

            # Limit x and y lists to 20 items
            self.xs = self.xs[-20:]
            self.ys1 = self.ys1[-20:]
            self.ys2 = self.ys2[-20:]
            self.ys3 = self.ys3[-20:]
            self.ys4 = self.ys4[-20:]

            # Plot values
            self.ax1.clear()
            self.ax1.plot(self.xs, self.ys1, color='red')
            self.ax1.set_ylabel(f'Temperature [\N{DEGREE SIGN}C]')
            self.ax1.set_title('AM2320 - Temperature')
            self.ax1.tick_params(axis='x', labelrotation=45)
            self.ax1.grid()

            self.ax2.clear()
            self.ax2.plot(self.xs, self.ys2, color='green')
            self.ax2.set_ylabel(f'Humidity [%]')
            self.ax2.set_title('AM2320 - Humidity')
            self.ax2.tick_params(axis='x', labelrotation=45)
            self.ax2.grid()

            self.ax3.clear()
            self.ax3.plot(self.xs, self.ys3, color='magenta')
            self.ax3.set_ylabel(f'Temperature [\N{DEGREE SIGN}C]')
            self.ax3.set_title('LPS25HB - Temperature')
            self.ax3.tick_params(axis='x', labelrotation=45)
            self.ax3.grid()

            self.ax4.clear()
            self.ax4.plot(self.xs, self.ys4, color='orange')
            self.ax4.set_ylabel(f'Pressure [hPA]')
            self.ax4.set_title('LPS25HB - Pressure')
            self.ax4.tick_params(axis='x', labelrotation=45)
            self.ax4.grid()

            self.fig.tight_layout()

    def wifi_choice(self):
        self.label_inter["text"] = ""
        self.proto = 'WiFi'
        if self.proto != self.protobuff:
            self.client_protocol_socket.send(b'WiFi')
            self.label_proto_choice["text"] = f"Choice: {self.proto}"
            print('New protocol choice: WiFi')
            self.protobuff = 'WiFi'
        else:
            self.label_inter["text"] = f"{self.proto} is actually choosen"

    def ble_choice(self):
        self.label_inter["text"] = ""
        self.proto = 'BLE'
        if self.proto != self.protobuff:
            self.client_protocol_socket.send(b'BLE')
            self.label_proto_choice["text"] = f"Choice: {self.proto}"
            print('New protocol choice: BLE')
            self.protobuff = 'BLE'
        else:
            self.label_inter["text"] = f"{self.proto} is actually choosen"

    def lora_choice(self):
        self.label_inter["text"] = ""
        self.proto = 'LoRa'
        if self.proto != self.protobuff:
            self.client_protocol_socket.send(b'LoRa')
            self.label_proto_choice["text"] = f"Choice: {self.proto}"
            print('New protocol choice: LoRa')
            self.protobuff = 'LoRa'
        else:
            self.label_inter["text"] = f"{self.proto} is actually choosen"


    def close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.quit()
            self.destroy()