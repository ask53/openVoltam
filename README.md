# OpenVoltam
-- THIS IS IN PROGRESS--

-- USE AT YOUR OWN RISK -- 

Open source software for running voltammetric tests and analyzing their results. Designed to work with the [RodeoStat from IO Rodeo](https://iorodeo.com/pages/rodeostat).

Installer available for Windows 10 and 11. 
Source code compatible with any computer with USB ports running python 3.12+. 

## License
This software is licensed for two main reasons:
1. To protect us from the situation in which a large corporation steals it, copyrights it, and then sues us for distributing it for free; and
2. To keep it open source, accessible, modifyable, and sharable.

We believe that everyone on this planet should have access to the tools to understand what is in the water that they drink. This software is our teeny, tiny contribution. To these ends, OpenVoltam is licensed under the [GNU General Public License version 3.0](https://github.com/ask53/openVoltam/blob/main/LICENSE). 

## Download 
All installers linked here are compatible with **Windows 10** and **Windows 11**. To run on any other operating system with python 3.12 or above, see the [Runing with python](https://github.com/ask53/openVoltam/blob/main/README.md#running-with-python) instructions below. 

### Stable releases
*We are still working on the features in our first stable release (and finding safe new homes for the many bugs that we encounter along the way). We aim to have it up by the middle of 2027. Please check back!*

### Test releases
- [Version 0.2](https://drive.google.com/file/d/1FdVPavv_b1hBFR1BqmzhgKYj29sY_EzB/view?usp=sharing) [Released: 06 Sep 2026] [Windows 10 & 11] (for beta testing)
- [Version 0.1](https://drive.google.com/file/d/1nNlRlT18m9fjE4lZMUhPBckaFG3FSlIe/view?usp=sharing) [Released: 28 Apr 2026] [Windows 10 & 11]  (for alpha testing, please let us know if you find bugs!)

### Running with python
This software ought to be able to be run on any operating system with python (although we haven't tested them all, so fair warning, there may be bugs!). It requires python 3.12 or above. We recommend avoiding virtual machines to avoid headaches with USB communications and port communications. But this software is free to use, so be free to make your own decisions :) To run with python, follow these steps:
1. Check your system's python version. If below 3.12, install version 3.12 or above. While you're at it:
    - Make sure that your python installation has a method of creating a virtual environment (these instructions use `venv` but any will do);
    - And a way of installing python packages (we'll use `pip` here, but its up to you!).
2. Get all the files onto your computer:
    - If you use github, clone this repository
    - If not, you can just download this whole repository and unzip it
3. Open up the `global_scripts > ov_globals.py` file in a text editor and make the following edits:
    1. Make sure that `PROC_RUN_FROM` is set to `PROC_RUN_FROM_PYTHON`
    2. Set `PROC_PYTHON_CMD` to whatever command your computer uses to run python
    3. Save your changes to `ov_globals.py` and close
4. Create a virtual environment. This is not necessary, but is highly recommended! With `venv` follow these steps:
    1. In a terminal, navigate (`cd`) to the main OpenVoltam folder (the folder that contains `OpenVoltam.py`)
    2. run `python -m venv venv`. You may have to replace "python" with whatever command your system uses for pytohn ('py', 'python3', 'python3.v' are all common). This creates a virtual environment in a folder called "venv"
5. Activate the venv. (Look up how to do this on your operating system. On linux, it is often `source venv/bin/activate`)
6. Install the relevant python packages
    1. With the venv activated, install all required packages: `pip install -r requirements.txt` This installs all packages except the potentiostat package from IORodeo.
    2. To install the potentiostat package:
        1. Navigate to the [potentiostat github repository](https://github.com/iorodeo/potentiostat)
        2. Get the code onto your machine:
            - If using github:
               1. Clone the repository
               2. Toggle into the `develop` branch
            - If not using github:
               1. Go to the linked repository above in a browser
               2. Switch the branch to `develop` (not `main`!)
               3. Download the files from github
               4. Unzip on your computer
         3. In a terminal, navigate into the `potentiostat > software > python > potentiostat` folder
         4. Make sure your virtual environment is still active and install as python package `pip install .`
7. Now that you have all the python packages downloaded and the code configured to your system's python installation, its time to launch OpenVoltam:
    a. In a terminal, navigate (`cd`) to the main OpenVoltam folder (the folder that contains `OpenVoltam.py`)
    b. Ensure that the virtual environment is active (`source venv/bin/activate`)
    c. Launch OpenVoltam! `python -m OpenVoltam`
   

## Notes for contributors
This project uses a version of IO Rodeo's potentiostat library that is not yet available on PyPi. (Note that there is no "potentiostat" package listed in the  requirements.txt file, even though it IS required to run OpenVoltam). The potentiostat library is only necessary for actually sending instructions to and receiving data from a device, not for running the rest of the GUI. So if you want to develop the interface but don't need to actually run tests, you are welcome to install the version on PyPi ('pip install iorodeo-potentiostat') and roll with that, although you may not be able to actually connect to a potentiostat device. If you do want to install the same version of the potentiostat library that this project uses to actually work with a device, you can clone the [IO Rodeo repository](https://github.com/iorodeo/potentiostat) to a local machine, switch from 'master' to 'develop' branch, and install locally (cd into .../potentiostat/software/python/potentiostat then use 'pip install .' if working with pip). Good luck!

## Building from python repository --> Windows executable --> Windows Installer
Follow these instructions if you want to build this python code into a Windows .exe file (uses PyInstaller to build .exe files for both the main process and the asynchronous processes) and step 8 to use InstallForce create a Microsoft Installer file that can be distributed.

### Create executable for async processes
1. Reset the settings.txt file to default values
2. Use PyInstaller to convert process.py into executable (cd into processes, run: py -m PyInstaller process.spec)
3. Move process.exe into 'external' folder
4. In global_scripts > ov_globals.py ajust to make sure async processes are running thru process.exe (comment out PROC_RUN_FROM = PROC_RUN_FROM_PYTHON and uncomment
PROC_RUN_FROM = PROC_RUN_FROM_EXE)
5. Run OpenVoltam.py, check async processes. If they work, continue. Otherwise, debug.

### Create executable to launch OpenVoltam
5. Use PyInstaller to convert OpenVoltam.py into executable (py -m PyInstaller OpenVoltam.spec)
6. In OpenVoltam > _internal, copy the 'external' folder. Paste it into the 'OpenVoltam' folder
7. Run OpenVoltam.exe and test

### Create installer
8. Use InstallForge to bundle this into an installer that can be distributed
