#include "time_tracker.h"

void TimerTracker::update() {
  unsigned long currentMillis = millis();

  // Check if the specified update interval has elapsed
  if (currentMillis - previousUpdateTime >= updateInterval) {
    previousUpdateTime = previousUpdateTime + updateInterval;  // Update the previous update time

    // Increment and store the usage time in EEPROM
    readUsageTime();
    usageTime++;
    EEPROM.update(address, usageTime);
  }
}


void TimerTracker::timePrint() {
  Serial.print("Use time: ");
  Serial.print(usageTime*5);
  Serial.println(" minutes");
}

void TimerTracker::start() {
  previousUpdateTime = millis();  // Set the initial update time
  readUsageTime();
}

void TimerTracker::reset() {
  EEPROM.update(address, 0);
  usageTime = 0;
}

int TimerTracker::getUsageTime() {
  return usageTime;
}

int TimerTracker::readUsageTime() {
  int toUpdate = EEPROM.read(address);
  usageTime = toUpdate;
  return toUpdate;
}

