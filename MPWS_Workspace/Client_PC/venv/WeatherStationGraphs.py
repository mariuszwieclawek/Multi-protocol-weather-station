import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class WeatherStationGraphs():
    def __init__(self, meas):
        self.meas = meas
        # Create figure for plotting
        self.fig, self.axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 7), label='Weather station characteristics')
        self.xs = []
        self.ys1 = []
        self.ys2 = []
        self.ys3 = []
        self.ys4 = []


    # This function is called periodically from FuncAnimation
    def animate(self, i):
        # Add x and y to lists
        self.xs.append(dt.datetime.now().strftime('%H:%M:%S'))
        self.ys1.append(self.meas.AM2320_TEMPERATURE)
        self.ys2.append(self.meas.AM2320_HUMIDITY)
        self.ys3.append(self.meas.LPS25HB_PRESSURE)
        self.ys4.append(self.meas.LPS25HB_TEMPERATURE)

        # Limit x and y lists to 20 items
        self.xs = self.xs[-20:]
        self.ys1 = self.ys1[-20:]
        self.ys2 = self.ys2[-20:]
        self.ys3 = self.ys3[-20:]
        self.ys4 = self.ys4[-20:]

        # Draw x and y lists
        self.axes[0, 0].clear()
        self.axes[0, 0].plot(self.xs, self.ys1)
        self.axes[0, 0].set_ylabel(f'Temperature [\N{DEGREE SIGN}C]')
        self.axes[0, 0].set_title('AM2320 - Temperature')
        self.axes[0, 0].grid()
        plt.sca(self.axes[0, 0])
        plt.xticks(rotation=45)

        self.axes[0, 1].clear()
        self.axes[0, 1].plot(self.xs, self.ys2)
        self.axes[0, 1].set_ylabel(f'Humidity [%]')
        self.axes[0, 1].set_title('AM2320 - Humidity')
        self.axes[0, 1].grid()
        plt.sca(self.axes[0, 1])
        plt.xticks(rotation=45)

        self.axes[1, 0].clear()
        self.axes[1, 0].plot(self.xs, self.ys3)
        self.axes[1, 0].set_ylabel(f'Temperature [\N{DEGREE SIGN}C[')
        self.axes[1, 0].set_title('LPS25HB - Temperature')
        self.axes[1, 0].grid()
        plt.sca(self.axes[1, 0])
        plt.xticks(rotation=45)

        self.axes[1, 1].clear()
        self.axes[1, 1].plot(self.xs, self.ys4)
        self.axes[1, 1].set_ylabel(f'Pressure [hPA]')
        self.axes[1, 1].set_title('LPS25HB - Pressure')
        self.axes[1, 1].grid()
        plt.sca(self.axes[1, 1])
        plt.xticks(rotation=45)

        self.fig.tight_layout()

    def graph_run(self):
        # ani = animation.FuncAnimation(self.fig, self.animate, interval=1000)
        plt.plot([1,2,3,4],[1,2,3,4])
        plt.show()
