"""
   Copyright (C) 2024 ETH Zurich. All rights reserved.
   Author: Sergei Vostrikov, ETH Zurich
   
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

# Specify time array in s (50 Hz sampling, 51 points)
time = np.array([0.  , 0.02, 0.04, 0.06, 0.08, 0.1 , 0.12, 0.14, 0.16, 0.18, 0.2 ,
                 0.22, 0.24, 0.26, 0.28, 0.3 , 0.32, 0.34, 0.36, 0.38, 0.4 , 0.42,
                 0.44, 0.46, 0.48, 0.5 , 0.52, 0.54, 0.56, 0.58, 0.6 , 0.62, 0.64,
                 0.66, 0.68, 0.7 , 0.72, 0.74, 0.76, 0.78, 0.8 , 0.82, 0.84, 0.86,
                 0.88, 0.9 , 0.92, 0.94, 0.96, 0.98, 1.  ])


# Specify relative pulse amplitudes
value = np.array([0.28      , 0.37146849, 0.62591439, 1.0466736 , 1.52667271,
                  1.64222491, 1.08131396, 0.81320634, 1.08727421, 1.26435095,
                  1.32538933, 1.18128374, 0.94817756, 0.81766342, 0.77304195,
                  0.77761592, 0.91133864, 1.10394458, 0.99962879, 0.90305052,
                  0.85318061, 0.81232899, 0.77225416, 0.73170681, 0.6910618 ,
                  0.65106826, 0.6125897 , 0.57658028, 0.5441228 , 0.51649961,
                  0.49530832, 0.47556755, 0.45385516, 0.43367219, 0.4156225 ,
                  0.39964261, 0.38553353, 0.3730854 , 0.36210489, 0.35241949,
                  0.34387657, 0.33634141, 0.32969512, 0.32383286, 0.31866214,
                 0.31410138, 0.31007863, 0.30653042, 0.30340077, 0.30064031,
                 0.2982054 ])



np.savez("./custom_pulses/custom_pulse.npz", value=value, time=time)