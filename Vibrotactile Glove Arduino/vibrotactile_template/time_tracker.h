/*
  Functions made to access and deal with the EEPROM using 32 bit counter
  Uses millis() for functionality with no wrapping cases, so the arduino can't be run for more than 47 or so days at a time.

  Created by Brody Skaufel, June 16th, 2023
*/
#ifndef time_tracker_h
#define time_tracker_h

#include <EEPROM.h>
#include <Arduino.h>

class TimerTracker {
private:
  const int address = 0;  // Address in EEPROM to store the usage time
  const unsigned long updateInterval = 300000;  // Update interval in milliseconds (5 minutes)
  unsigned long previousUpdateTime = 0;  // Variable to store the previous update time
  int usageTime = 0; //Works in intervals of 5 mins

  int readUsageTime();
public:
  void update(); //Must call in loop()
  void start();
  int getUsageTime();
  void reset();
  void timePrint();
};

#endif
