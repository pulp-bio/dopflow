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

import numpy as np
import os
from scipy.interpolate import PchipInterpolator

def periodic_wrap_fn(t, period):
    """ Wrapp all t > period to t-N*period
    Args:
        t (np.array)  : the time vector
        period (float): wrapping period
        
    Returns:
        np.array: wrapped time vector
    """
    wrapper = lambda x: x-np.floor(x/period)*period
    identity = lambda x: x
    return np.piecewise(t, [(t > 0), (t <= 0)], [wrapper, identity])


class PulseWave():
    def __init__(self, time, value, bpm: float = 60, amplitude: float = 60):
        self.bpm = bpm
        self.amplitude = amplitude
        self.load_pulse(time, value)


    def load_pulse(self, time, value):
        assert len(time) == len(value)
        #normalized time and amplitude
        self.time_array = time/np.max(time)
        self.value_array = value/np.max(value)

        self.set_bpm_amp(self.bpm,self.amplitude)

    def set_bpm_amp(self, bpm: float = 60, amplitude: float = 1):
        """  Wrapp all t > period to t-N*period
        Args:
            bpm (float )  : the pulse rate in bpm
            amplitude (float): amplitude of the pulse
        """
        self.bpm = bpm
        self.amplitude = amplitude

        if abs(amplitude) < 1e-8:
            self.flow_function_cyclic = lambda t: t*0
        else:
            T_pulse = 60/bpm # -> [s]
            # function to wrap time > T_pulse
            wrap_fn = lambda t: periodic_wrap_fn(t,T_pulse)

            t = self.time_array*T_pulse
            v = self.value_array*amplitude
            # Interpolate data
            flow_function = PchipInterpolator(t, np.log(v))
            self.flow_function_cyclic = lambda t: np.exp(flow_function(wrap_fn(t)))

    def __call__(self, time):
       return self.flow_function_cyclic(time)

class HeartRateWave(PulseWave):
    
    def __init__(self, heart_rate: float = 60, amplitude: float = 1):
        t_hr = np.array([0, 0.3, 0.4, 0.45, 0.5, 0.6, 0.65, 0.9, 1])
        v_hr = np.array([.2,  .2,  1, .575, .6, .2, .4, .2, .2])
        super().__init__(t_hr,v_hr,heart_rate,amplitude)
        self.load_pulse = None

    def set_hr(self, heart_rate: float = 60, amplitude: float = 1):
        """  Wrapp all t > period to t-N*period
        Args:
            heart_rate (float )  : the heart rate in bpm
        """
        self.set_bpm_amp(heart_rate, amplitude)

def save_pulse_file(file_name, time_array, value_array):
    # Check filename
    if os.path.isfile(file_name):
        for i in range(100):
            new_name = file_name[:-4] + str(i) + '.npz'
            if not os.path.isfile(new_name):
                break
        file_name = new_name
    np.savez(file_name[:-4], 
             time=time_array,
             value=value_array)
 
if __name__ == '__main__':
    save_pulse_file("./saw_tooth.npz",


            np.array([0.,.1,.2,.3,.4,.5,.6,.7,.8,.9, 1.  ]),
            np.array([.01,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]))