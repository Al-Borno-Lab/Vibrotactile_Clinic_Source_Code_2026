This is meant to be loaded onto an Arduino LilyPad 328 microcontroller.
"vibrotactile_template.ino" is what should be written to the controller,
but the header files and cpp files included in this folder must be present in the same location as this file.
 
There is a large block of "EDITABLE VARIABLES" that you will likely need to adjust.
pattern_mode switches between "RVS", "All-on", and "All_off"
RVS alternates between fingertips at a switching rate of 1hz.
All-on stimulates all fingers continuously.
All_off does not produce any output. This is useful for pre-clinical fitting and experiment setup.

the "fingers" dictionary refers to which output channels on the arduino is connected to which finger.
For example, if you used output pins 2,4,5,7,8 for the fingers, then
fingers[5] = {2,4,5,7,8}; would be appropriate. Test your gloves by running the code to be sure.

you may experiment with the other variables if you wish to, but they are currently set to the conditions used in the clinical pilot.

