import threading
import time
import tkinter as tk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AntennaAlignmentApp:
    
    # Initialize antenna angles
    mobile_angle = 0
    base_angle = 0
    max_gain_index = 0
    
    def __init__(self, master):
        self.master = master
        self.plot_frame = tk.Frame(master)
        self.plot_frame.pack()
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()
        self.master.title("Antenna Alignment")
        
        self.center = (200, 200)  # Center of the circle
        self.radius = 100  # Radius of the circle
        self.gain_max_angle = 0
        self.triangle_coords  = [(190.0,217.32050807568877), (210.0,217.32050807568877), (200.0,182.67949192431123)]
        self.mobile_coords = [(190, 290), (210, 310)]
        
        # Create GUI elements
        self.mobile_antenna = self.canvas.create_rectangle (self.mobile_coords, fill='blue')
        self.base_antenna = self.canvas.create_polygon(self.triangle_coords, fill='red')
        self.mobileTextId = self.canvas.create_text(205, 210, text="Omni", fill="blue")
        self.baseTextId = self.canvas.create_text(210, 210, text="Base Station", fill="red")
        
        self.ray_lines = []
        self.gain_pattern = 0
        self.prev_max_gain_index = 0
        
        self.canvas.tag_bind(self.mobile_antenna, '<B1-Motion>', self.move_mobile_antenna) 
        
        self.plot_setup()
        
        while True:
            self.new_signal(self.mobile_angle)
            time.sleep(0.1)
          
    def move_mobile_antenna(self, event):
        x, y = event.x, event.y
        # Calculate the angle between the center and the current position
        self.mobile_angle = np.arctan2(y - self.center[1], x - self.center[0])
        # Calculate the new position on the circumference of the circle
        new_x = self.center[0] + self.radius * np.cos(self.mobile_angle)
        new_y = self.center[1] + self.radius * np.sin(self.mobile_angle)
        # Move the mobile antenna to the new position
        self.canvas.coords(self.mobile_antenna, new_x - 5, new_y - 5, new_x + 5, new_y + 5)
        # Update text and rays
        self.update_text_and_rays(new_x, new_y)
        # self.new_signal()
    
    def update_text_and_rays(self, new_x, new_y):
        self.canvas.delete(self.mobileTextId)
        self.mobileTextId = self.canvas.create_text(new_x+25, new_y+25, text="Omni", fill="blue")
        # Update rays
        for line in self.ray_lines:
            self.canvas.delete(line)
        self.ray_lines = []
        for angle in np.linspace(-np.pi, np.pi, 90):
            end_x = 200 + 400 * np.cos(angle)
            end_y = 200 + 400 * np.sin(angle)
            ray_line = self.canvas.create_line(new_x, new_y, end_x, end_y, fill='gray')
            self.ray_lines.append(ray_line)
          
    def new_signal(self,mobile_angle):
        self.signal_length = 10 
        self.signal = np.random.randint(2, size=self.signal_length)
        self.noisy_signal = self.add_noise(self.signal * 2 - 1)  # Convert 0s 
        angles, self.gain_pattern = self.calculate_gain_pattern()
        self.received_signal = np.convolve(self.noisy_signal, self.gain_pattern, mode='same')  # Receive signal at base station antenna
        self.detect_signal(self.received_signal,mobile_angle)  # Detect signal and align base station antenna
        self.plot_signal(self.signal, self.received_signal, self.noisy_signal, angles)
        plt.pause(0.1)
          
    def move_base_antenna(self,base_angle):
        # Update the rotation angle
        self.base_angle = base_angle
        self.canvas.delete(self.base_antenna)  # Delete the old triangle
        self.triangle_coords = self.rotate_point(self.triangle_coords, self.base_angle)
        self.base_antenna = self.canvas.create_polygon(self.triangle_coords, fill='red')  # Redraw the triangle
    
    def rotate_point(self, point, angle):
        ox, oy = 200, 200  # Center of rotation (for example)
        (x1, y1),(x2,y2),(x3,y3) = point
        radians = np.radians(angle)
        qx1 = ox + np.cos(radians) * (x1 - ox) - np.sin(radians) * (y1 - oy)
        qy1 = oy + np.sin(radians) * (x1 - ox) + np.cos(radians) * (y1 - oy)
        qx2 = ox + np.cos(radians) * (x2 - ox) - np.sin(radians) * (y2 - oy)
        qy2 = oy + np.sin(radians) * (x2 - ox) + np.cos(radians) * (y2 - oy)
        qx3 = ox + np.cos(radians) * (x3 - ox) - np.sin(radians) * (y3 - oy)
        qy3 = oy + np.sin(radians) * (x3 - ox) + np.cos(radians) * (y3 - oy)
        return [(qx1, qy1),(qx2, qy2),(qx3, qy3)]
       
    def add_noise(self, signal):
        # Add Rayleigh fading
        rayleigh_noise = np.random.rayleigh(0.5, size=len(signal))
        # Add AWGN (Additive White Gaussian Noise)
        awgn_noise = np.random.normal(0, 0.1, size=len(signal))
        # Add noise to the signal
        return signal + rayleigh_noise + awgn_noise
     
    def calculate_gain_pattern(self):
        self.angles = np.linspace(-np.pi, np.pi, 360)
        self.plot(self.angles)
        plt.pause(0.1)
        return self.angles, np.cos(self.angles - self.base_angle)**2/np.exp(1*np.abs(self.angles))
    
    def detect_signal(self, received_signal,mobile_angle):
        self.prev_max_gain_index = self.max_gain_index
        print(self.prev_max_gain_index)
        self.max_gain_index = np.argmax(received_signal*np.cos(mobile_angle-self.base_angle))
        self.base_angle = self.max_gain_index * (2 * np.pi / len(received_signal))
        self.move_base_antenna(self.base_angle)
        if((self.max_gain_index < self.prev_max_gain_index+5)and(self.max_gain_index > self.prev_max_gain_index-5)):
            self.move_base_antenna(self.base_angle+1)
        else: self.move_base_antenna(self.base_angle-1)

    def plot_setup(self):
        
        # Create a figure and axes for subplots
        fig, self.axs = plt.subplots(2, 2, figsize=(10, 8))

        # Plot each graph in the corresponding subplot
        
        self.axs[0, 0].set_title('Gain of Directional')
        self.axs[0, 0].set_xlabel('angle')
        self.axs[0, 0].set_ylabel('Gain')
        self.line1, = self.axs[0, 0].plot([], [])  # Create an empty line

        self.axs[0, 1].set_title('Signal provided')
        self.axs[0, 1].set_xlabel('time')
        self.axs[0, 1].set_ylabel('value')
        self.line2, = self.axs[0, 1].plot([], [])  # Create an empty line

        self.axs[1, 0].set_title('Noisy Signal')
        self.axs[1, 0].set_xlabel('time')
        self.axs[1, 0].set_ylabel('value')
        self.line3, = self.axs[1, 0].plot([], [])  # Create an empty line

        self.axs[1, 1].set_title('Signal received')
        self.axs[1, 1].set_xlabel('time')
        self.axs[1, 1].set_ylabel('value')
        self.line4, = self.axs[1, 1].plot([], [])  # Create an empty line

        # Adjust layout
        plt.tight_layout()
        self.signal_data = []
        self.received_data = []
        self.time_data = []
                     
    def plot(self, angles):
          
        self.line1.set_data(np.degrees(angles), self.gain_pattern)  # Update the data of the line
        self.axs[0,0].relim()
        self.axs[0,0].autoscale()  # Adjust the axis limits
        plt.draw()  # Redraw the plot
        
    def plot_signal(self,signal,received_signal,noisy_signal,angles):
        
        # Add current time and signal value to the data lists
        # current_time = time.time()
        time = np.linspace(0, 10, 10)
        
        self.line2.set_data(time, signal)  # Update the data of the line
        self.axs[0,1].relim()
        self.axs[0,1].autoscale()  # Adjust the axis limits
        
        self.line3.set_data(time, noisy_signal)  # Update the data of the line
        self.axs[1,0].relim()
        self.axs[1,0].autoscale()  # Adjust the axis limits
        
        self.line4.set_data(np.degrees(angles), received_signal)  # Update the data of the line
        self.axs[1,1].relim()
        self.axs[1,1].autoscale()  # Adjust the axis limits
        plt.draw()  # Redraw the plot

def main():
    root = tk.Tk()
    AntennaAlignmentApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

