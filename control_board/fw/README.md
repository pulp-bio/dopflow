# Flashing the firmware to the control board

### 1. Download STM32CubeIDE
Download and install the latest version **1.12.1** of STM32CubeIDE from the [ ST website](https://www.st.com/en/development-tools/stm32cubeide.html#get-software).

### 2. Create a new project
- In STM32CubeIDE go to File > New > STM32 Project from an Existing STM32CubeMX Configuration File (.ioc).<br>
- Select the file in `phantom_control/phantom_control.ioc` and press Finish.<br>
- Next, overwrite the files in the folders `Core/*` and `USB_DEVICE/*` (USB interface files) from this repository. 
For this, drag and drop both folders to the newly created project located in `C:\Users\USERNAME\STM32CubeIDE\workspace_1.12.1\phantom_control`. Select Copy files and folders, click OK and then Overwrite All.<br>
### 3. Build and Flash the project
- You can now build the project, and flash it to the STM32F3DISCOVERY board plugged into the control PCB. <br>
- To control the motor and run a custon flow profile, use the GUI in `./software` folder of the repository.

# Authors
- The initial control board firmware was developed by [Nazemtsev Ilia](https://www.linkedin.com/in/ilia-nazemtsev/). Subsequent updates and major improvements were implemented by [Josquin Tille](https://www.linkedin.com/in/josquin-tille-829a341a7/).

# License
The files in the `control_board/fw/` directory contains third-party sources that come with their own licenses. See the respective folders and source files' headers for the licenses used.
The code developed at IIS comes under Apache License 2.0 (`Apache-2.0`) (see `control_board/LICENSE`).