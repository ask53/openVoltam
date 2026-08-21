# openVoltam
-- THIS IS IN PROGRESS--

-- USE AT YOUR OWN RISK -- 

Open source software, compatible only with Windows 10 and 11. For running voltammetric tests and analyzing their results. Designed to work with the [RodeoStat from IO Rodeo](https://iorodeo.com/pages/rodeostat).

## License
This software is licensed for two main reasons:
1. To protect us from the situation in which a large corporation steals it, copyrights it, and then sues us; and
2. To keep it open source, accessible, modifyable, and sharable.

To these ends, OpenVoltam is licensed under the [GNU General Public License version 3.0](https://github.com/ask53/openVoltam/blob/main/LICENSE). 

## Download 
All releases compatible with **Windows 10 and 11**. 

If you *need* access on a different operating system, please contact us.

### Stable releases
Ruh roh, please come back later once things stabilize a bit!

### Test releases
- [Version 0.1](https://drive.google.com/file/d/1nNlRlT18m9fjE4lZMUhPBckaFG3FSlIe/view?usp=sharing) (for alpha testing, please let us know if you find bugs!) [Windows 10 & 11]  

## Notes for contributors
This project uses a version of IO Rodeo's potentiostat library that is not yet available on PyPi. (See local link in requirements.txt file). 
The potentiostat library is only necessary for actually sending instructions to and receiving data from a device, not for running the rest of the GUI, you are welcome to install the version on PyPi ('pip install iorodeo-potentiostat') and roll with that, although you may not be able to actually connect to a device. If you do want to install the same version of the potentiostat library that this project currently using to actually work with a rodeostat device, you can clone the [IO Rodeo repository](https://github.com/iorodeo/potentiostat) to a local machine, switch from 'master' to 'develop' branch, and install locally (cd into .../potentiostat/software/python/potentiostat then use 'pip install .' if working with pip). Good luck!

## Building from repository --> Windows executable --> Windows Installer
Follow these instructions if you want to build this python code into a Windows .exe file (uses PyInstaller to build .exe files for both the main process and the asynchronous processes) and step 8 to use InstallForce create a Microsoft Installer file that can be distributed.

### Create executable for async processes
1. Use PyInstaller to convert process.py into executable (cd into processes, run: py -m PyInstaller process.spec)
2. Move process.exe into 'external' folder
3. In global_scripts > ov_globals.py ajust to make sure async processes are running thru process.exe
4. Run OpenVoltam.py, check async process. If they work, continue. Otherwise, adjust.

### Create executable to launch OpenVoltam
5. Use PyInstaller to convert OpenVoltam.py into executable (py -m PyInstaller OpenVoltam.spec)
6. In OpenVoltam > _internal, copy the 'external' folder. Paste it into the 'OpenVoltam' folder
7. Run OpenVoltam.exe and test

### Create installer
8. Use InstallForge to bundle this into an installer that can be distributed
