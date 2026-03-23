# openVoltam
-- THIS IS IN PROGRESS AND DOES NOT YET WORK TO RUN A COMPLETE ANALYSIS.--
-- USE AT YOUR OWN RISK --

Open source software for running voltammetric tests and analyzing their results. Designed to work with the RodeoStat from IO Rodeo, https://iorodeo.com/pages/rodeostat

## Installation (for now)
To run the most up to date version of OpenVoltam follow these steps:
1. Download the zip file.
2. Unzip it
3. Once unzipped, run OpenVoltam.exe from inside the resulting folder.

## Notes for contributors
This project uses a version of IO Rodeo's potentiostat library that is not yet available on PyPi. (See local link in requirements.txt file). 
The potentiostat library is only necessary for actually sending instructions to and receiving data from a device, not for running the rest of the GUI, you are welcome to install the version on PyPi ('pip install iorodeo-potentiostat') and roll with that, although you may not be able to actually connect to a device. If you do want to install the same version of the potentiostat library that this project currently using to actually work with a rodeostat device, you can clone the IO Rodeo repository [https://github.com/iorodeo/potentiostat] to a local machine, switch from 'master' to 'develop' branch, and install locally (cd into .../potentiostat/software/python/potentiostat then use 'pip install .' if working with pip). Good luck!
