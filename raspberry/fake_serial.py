import time
import random
from threading import Thread, Lock
import matplotlib.pyplot as plt
from collections import deque

class FakeSerial:
    """
    Simulates an Arduino serial port.
    - Generates logs to a file.
    - Stores last LCR values.
    - Optional real-time plot of intensities.
    """

    def __init__(self, log_file="fake_serial.log", plot=True, max_points=100):
        self.lock = Lock()
        self.log_file = log_file
        self.plot = plot
        self.max_points = max_points
        self.running = True
        
        self.L_values = deque(maxlen=max_points)
        self.C_values = deque(maxlen=max_points)
        self.R_values = deque(maxlen=max_points)
        self.times = deque(maxlen=max_points)
        
        if self.plot:
            plt.ion()
            self.fig, self.ax = plt.subplots()
            self.l_line, = self.ax.plot([], [], 'r-', label='L')
            self.c_line, = self.ax.plot([], [], 'g-', label='C')
            self.r_line, = self.ax.plot([], [], 'b-', label='R')
            self.ax.set_ylim(0, 255)
            self.ax.set_xlim(0, max_points)
            self.ax.legend()
            self.ax.set_title("Simulated LCR Intensities")
            self.ax.set_xlabel("Frames")
            self.ax.set_ylabel("Intensity")
    
    def write(self, message_bytes):
        """
        Simulate writing to Arduino serial port.
        Parse message LCRXXXCXXXRXXX and log it.
        """
        message = message_bytes.decode().strip()
        with self.lock:
            #Log to file
            with open(self.log_file, "a") as f:
                f.write(f"{time.time():.3f} {message}\n")
            
            #Parse LCR values
            try:
                L = int(message[1:4])
                C = int(message[5:8])
                R = int(message[9:12])
            except Exception:
                L = C = R = 0
            
            self.L_values.append(L)
            self.C_values.append(C)
            self.R_values.append(R)
            self.times.append(time.time())
            
            #Print fake serial
            print(f"[FAKE SERIAL] {message}")
            
            #Update plot
            if self.plot:
                self.update_plot()
    
    def update_plot(self):
        self.l_line.set_ydata(list(self.L_values))
        self.c_line.set_ydata(list(self.C_values))
        self.r_line.set_ydata(list(self.R_values))
        self.l_line.set_xdata(range(len(self.L_values)))
        self.c_line.set_xdata(range(len(self.C_values)))
        self.r_line.set_xdata(range(len(self.R_values)))
        
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def close(self):
        self.running = False
        if self.plot:
            plt.ioff()
            plt.show()
