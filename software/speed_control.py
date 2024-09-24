"""
   Copyright (C) 2024 ETH Zurich. All rights reserved.
   Author: Josquin Tille, ETH Zurich
   
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   SPDX-License-Identifier: Apache-2.0
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import numpy as np
import threading

import time
import serial.tools.list_ports

from heart_rate import PulseWave, HeartRateWave

BAUD_RATE = 115200

def get_ports():
    ports = serial.tools.list_ports.comports()
    port_list = []
    desc_list = []

    for port, desc, hwid in sorted(ports):
        port_list += [port]
        desc_list += [desc]

    return port_list, desc_list

class MyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Phantom Controller")

        # COM Port section
        com_frame = ttk.LabelFrame(root, text="COM Port Control")
        com_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        self.port_var = tk.StringVar()
        port_label = ttk.Label(com_frame, text="Select COM Port:")
        port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_list, port_options = get_ports()
        self.port_combobox = ttk.Combobox(com_frame, textvariable=self.port_var, values=port_options, state="readonly")
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.open_button = ttk.Button(com_frame, text="Open COM", command=self.open_com)
        self.open_button.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.is_port_open = False


        # Graph section
        graph_frame = ttk.LabelFrame(root, text="Graph Control")
        graph_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        # Select Manual or pulse
        self.speed_mode_var = tk.StringVar(value="Manual")
        mode_radio1 = ttk.Radiobutton(graph_frame, text="Set manual speed", variable=self.speed_mode_var, value="Manual", command=self.update_all)
        mode_radio1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)


        mode_radio2 = ttk.Radiobutton(graph_frame, text="Send blood flow pulses", variable=self.speed_mode_var, value="BFP", command=self.update_all)
        mode_radio2.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        #mode_radio2["state"] = "disabled"
        mode_radio3 = ttk.Radiobutton(graph_frame, text="Custom Pulses", variable=self.speed_mode_var, value="Custom", command=self.update_all)
        mode_radio3.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.load_file_button = ttk.Button(graph_frame, text="Load File", command=self.load_pulse_file)
        self.load_file_button.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)


        # Slider amplitude
        self.MAX_SPEED = 1 # m/s
        slider_frame = ttk.Frame(graph_frame)
        slider_frame.grid(row=2, column=0, rowspan=2, columnspan=4, padx=5, pady=5, sticky=tk.W)

        self.slider_amp_var = tk.DoubleVar(value=0)
        self.slider_amp_var.trace('w', self.update_amplitude)
        slider_amp_label = ttk.Label(slider_frame, text="Amplitude:")
        slider_amp_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)


        self.slider_amp = ttk.Scale(slider_frame, from_=0, to=self.MAX_SPEED, variable=self.slider_amp_var, orient=tk.HORIZONTAL, command=self.update_slider_amp)
        self.slider_amp.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        slider_amp_entry = ttk.Entry(slider_frame, width=5, textvariable=self.slider_amp_var)
        slider_amp_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # hr slider
        self.slider_freq_var = tk.DoubleVar(value=60)
        self.slider_freq_var.trace('w', self.update_freq)
        slider_freq_label = ttk.Label(slider_frame, text="Frequency [bpm]:")
        slider_freq_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        slider_freq = ttk.Scale(slider_frame, from_=10, to=120, variable=self.slider_freq_var, orient=tk.HORIZONTAL, command=self.update_slider_freq)
        slider_freq.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        slider_freq_entry = ttk.Entry(slider_frame, width=5, textvariable=self.slider_freq_var)
        slider_freq_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        # Unit
        unit_frame = ttk.Frame(graph_frame)
        unit_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        unit_label = ttk.Label(unit_frame, text="Select Unit:")
        unit_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.unit_var = tk.StringVar(value="m/s")
        unit_radio1 = ttk.Radiobutton(unit_frame, text="Motor speed [RPM]", variable=self.unit_var, value="RPM", command=self.set_to_rpm)
        unit_radio1.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        #unit_radio1["state"] = "disabled"

        unit_radio2 = ttk.Radiobutton(unit_frame, text="Flow speed [m/s]", variable=self.unit_var, value="m/s", command=self.set_to_ms)
        unit_radio2.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        #unit_radio2["state"] = "disabled"
        self._is_rpm = False

        TUBE_AREA_RATIO     = 45.76777
        DISTANCE_PER_TURN   = 4e-3
        self.ms_rpm_ratio = TUBE_AREA_RATIO*DISTANCE_PER_TURN/60

        

        # send data button
        self.send_button = ttk.Button(graph_frame, text="Start ▶️", command=self.send_to_com_button_call)
        self.send_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        self.is_data_sending = False
        self.send_button["state"] = "disabled"

        # Plot section
        self.is_plotting = False
        bpm = self.slider_freq_var.get()
        amp = self.slider_amp_var.get()
        self.pulse = HeartRateWave(bpm,amp)
        self.custom_pulse = PulseWave(self.pulse.time_array,self.pulse.value_array, bpm, amp)
        plot_frame = ttk.LabelFrame(root, text="Speed profile")
        plot_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        self.figure, self.ax = Figure(figsize=(5, 2), dpi=100, layout='tight', facecolor="#E4E5E4"), None
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.graph_max_time = 3.5
        self.GRAPH_NUM_POINT= 1200
        # Serial Port Data section
        serial_frame = ttk.LabelFrame(root, text="Serial Port Data")
        serial_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        self.serial_data_text = tk.Text(serial_frame, height=7, width=50, state="disabled")
        self.serial_data_text.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Start a thread to get serial port data 
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()

        # Thread to send the pulse periodically
        self.pulse_thread = threading.Thread(target=self.send_pulse_data)
        self.pulse_thread.daemon = True
        self.pulse_thread.start()

        # Thread to check if com is closed
        self.com_check = threading.Thread(target=self.com_check)
        self.com_check.daemon = True
        self.com_check.start()

        # Initial plot
        self.plot_function()

    def open_com(self):
        if not self.is_port_open:
            selected_port = self.port_list[self.port_combobox.current()]
            print(selected_port)
            if self.port_var.get() != "":
                # enable button
                self.open_button["text"] = "Close COM"
                self.send_button["state"] = "normal"
                # open port
                self.ser = serial.Serial(selected_port, BAUD_RATE)

                self.is_port_open = True
                self.update_serial_data("Connected to "+selected_port+"\n")
                self.send_to_com_button_call()
        else:
            self.open_button["text"] = "Open COM"
            #send button off
            if self.is_data_sending:
                self.send_to_com_button_call()
            self.send_button["state"] = "disabled"
            # close serial
            self.ser.close()
            self.is_port_open = False
            self.update_serial_data("Disconnected\n\n")
            


    def close_com(self):
        #enable button
        self.open_button["state"] = "normal"
        self.close_button["state"] = "disabled"
        # close serial
        self.ser.close()

    def scan_port(self):
        self.port_list, self.port_combobox['value'] = get_ports()

    def send_to_com_button_call(self):
        if not self.is_data_sending:
            self.is_data_sending = True
            self.send_button["text"] = "Stop ⏸️"
            active_speed_mode = self.speed_mode_var.get()
            speed = self.slider_amp_var.get()
            unit = self.unit_var.get()
            if active_speed_mode == "Manual":
                self.send_speed(speed, unit)

        else:
            self.is_data_sending = False
            self.send_speed(0)
            self.send_button["text"] = "Start ▶️"


    def send_speed(self, speed, unit: str="m/s"):
        #motor speed is int step per microsec
        STEPS_PER_TURN = 200
        if abs(speed) < 1e-8:
            mot_speed = 0
        else:
            mot_speed = 1e6/speed/STEPS_PER_TURN*60


        if unit == "RPM":
            pass
        elif unit == "m/s":
            mot_speed *= self.ms_rpm_ratio
        else:
            raise NotImplementedError(f"{unit} is not a valid unit")

        message = str(int(mot_speed+.5))+'\n'
        try:
            self.ser.write(bytes(message, 'utf-8'))
        except: # so that it doesn't crash if disconnected
            return 0
        else:
            return 1
            

    def update_slider_amp(self, value):
        if self.unit_var.get()=="m/s":
            value = np.round(float(value), 2)
        else:
            value = int(float(value))
        self.slider_amp_var.set(value)


    def update_slider_freq(self, value):
        value = int(float(value))
        self.slider_freq_var.set(value)
        self.plot_function()

    def plot_function(self):
        x = np.linspace(0, self.graph_max_time, self.GRAPH_NUM_POINT)
        active_speed_mode = self.speed_mode_var.get()

        if active_speed_mode == "Manual":
            y=np.ones_like(x)*self.slider_amp_var.get()
        elif active_speed_mode == "BFP":
            y = self.pulse(x)
        else:
            y = self.custom_pulse(x)

        if self.ax is None:
            self.ax = self.figure.add_subplot(111)
        else:
            self.ax.clear()

        try:
            self.ax.plot(x, y)
            self.ax.grid(True)
            self.ax.set_title("Speed profile")
            self.ax.set_xlabel("Time [s]")
            self.ax.set_ylabel("Speed ["+self.unit_var.get()+"]")
            if self.unit_var.get()=="m/s":
                self.ax.set_ylim((-.04, self.MAX_SPEED*1.1))
            else:
                self.ax.set_ylim((-.04, self.MAX_SPEED/self.ms_rpm_ratio*1.1))
            self.canvas.draw()
        except:
            print("ERROR printing graph")

    def read_serial_data(self):
        data = 0
        while True:
            if self.is_port_open:
                try:
                    bytesToRead = self.ser.inWaiting()
                    data = self.ser.read(bytesToRead)
                    self.ser.flushInput()
                except:
                    pass #disconnect while reading
                else:
                    self.update_serial_data(data.decode('utf-8'))
                time.sleep(.25)
            else:
                time.sleep(1)

    def update_serial_data(self, data):
        data=data.replace('\r', '')
        self.serial_data_text.configure(state='normal')
        self.serial_data_text.insert(tk.END, data)
        self.serial_data_text.configure(state='disabled')
        self.serial_data_text.see(tk.END)

    def update_all(self, *args):
        self.plot_function()

        active_speed_mode = self.speed_mode_var.get()
        speed = self.slider_amp_var.get()
        if self.is_data_sending and active_speed_mode == "Manual":
            unit = self.unit_var.get()
            self.send_speed(speed, unit)

        self.update_freq()

    def set_to_ms(self):
        self.slider_amp['to'] = self.MAX_SPEED
        if self._is_rpm:
            new_speed = self.slider_amp_var.get() * self.ms_rpm_ratio
            new_speed = np.round(new_speed,2)
            self.slider_amp_var.set(new_speed) 
            self._is_rpm = False
    def set_to_rpm(self):
        self.slider_amp['to'] = self.MAX_SPEED/self.ms_rpm_ratio
        if not self._is_rpm:
            new_speed = self.slider_amp_var.get() / self.ms_rpm_ratio
            new_speed = int(new_speed)
            self.slider_amp_var.set(new_speed) 
            self._is_rpm = True

    def send_pulse_data(self):
        SAMPLING_TIME = 20e-3 #s
        while True:
            speed_mode = self.speed_mode_var.get()
            if self.is_data_sending and speed_mode != "Manual":
                t = time.time()
                speed = self.pulse(t) if speed_mode == "BFP" else self.custom_pulse(t)
                self.send_speed(speed, self.unit_var.get())
                if not self.is_data_sending:
                    self.send_speed(0)
                if abs(speed)>1e-8:
                    time.sleep(SAMPLING_TIME)
                else:
                    time.sleep(1)
            
            else:
                time.sleep(1)

    def update_amplitude(self, *args):
        self.is_plotting=True
        active_speed_mode = self.speed_mode_var.get()
        try: # test if the new value is valid
            self.slider_amp_var.get()
        except:
            self.slider_amp_var.set(0)
        amplitude = self.slider_amp_var.get()
        if amplitude < 0:
            self.slider_amp_var.set(0)
        elif amplitude > self.MAX_SPEED:
            if self.unit_var.get()=="m/s":
                self.slider_amp_var.set(self.MAX_SPEED)
            elif amplitude > self.MAX_SPEED/self.ms_rpm_ratio:
                self.slider_amp_var.set(self.MAX_SPEED/self.ms_rpm_ratio)


        if active_speed_mode == "Manual":
            self.update_all()

        else:
            amplitude = self.slider_amp_var.get()
            bpm = self.slider_freq_var.get()
            self.pulse.set_hr(bpm, abs(amplitude))
            self.custom_pulse.set_bpm_amp(bpm, abs(amplitude))
            self.plot_function()
            if abs(amplitude)<=1e-8:
                self.send_speed(0)

        self.is_plotting=False

    def update_freq(self, *args):
        try: # test if the new value is valid
            self.slider_freq_var.get()
        except:
             self.slider_freq_var.set(60)

        active_speed_mode = self.speed_mode_var.get()
        if active_speed_mode != "Manual":
            amplitude = self.slider_amp_var.get()
            bpm = self.slider_freq_var.get()
            self.pulse.set_hr(bpm, abs(amplitude))
            self.custom_pulse.set_bpm_amp(bpm, abs(amplitude))
            self.plot_function()

    def com_check(self):
        while True:
            port_list, port_desc = get_ports()
            #disconection handling
            if self.port_var.get() not in port_desc and self.port_var.get() != "":
                if self.is_port_open:
                    self.open_com() # close if open
                self.port_var.set("")
                self.scan_port()

            if  set(self.port_combobox['value']) != set(port_desc):
                self.scan_port()

            time.sleep(.2)

    def load_pulse_file(self):
        self.send_speed(0)
        filetypes = (
            ('Numpy array files', '*.npz'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(title='Load files', filetypes=filetypes)
        if filename != '':
            file_data = np.load(filename)
            
            TIME_NAME = "time"
            VALUE_NAME = "value"
            if not TIME_NAME in file_data.keys() and  not VALUE_NAME in file_data.keys():
                self.update_serial_data("Not a valid file format\n")
            else:
                self.custom_pulse.load_pulse(file_data[TIME_NAME], file_data[VALUE_NAME])
        
        self.update_all()


if __name__ == "__main__":
    root = tk.Tk()
    app = MyGUI(root)
    root.resizable(False, False)  # Don't allow window resizing
    root.mainloop()
