This is the python code that we used to track motor patterns during the clinical pilot.
It also makes a "nice" GUI for monitoring recording intervals.

To run, open an anaconda console, navigate to this folder, and then run 
"python.exe ClinicalGUI.py"

You will need to record the COM port that your arduino device is on (in the arduino IDE) and change
line 30:
ACOM = 'COM7'
to your port

I would also advice changing line 28 to reflect your participant id.

The python package requirements can be deduced from the py file, but briefly:

conda install pip
pip install pyserial
pip install FreeSimpleGUI
pip install numpy
pip install pandas
pip install matplotlib
pip install keyboard

should be sufficient. 