#include "pattern_tracker.h"
#include "time_tracker.h"
#include <Arduino.h>
// Template use for vibrotactile gloves
// Created November 17th, 2023
// Author: Brody Skaufel
//
// A template to be used to upload data for the arduino sleeves and gloves.
// Tracks usage time to an increment of 5 minutes and applies differing patterns.
// 
// WHEN UPLOADING CODE TO SLEEVE make sure nothing is connected to pins 0 or 1 (Upload will fail)
//
/* 
Current pattern modes are...
  in_order, //All motors in order one at a time
  one_per,   // random one at a time
  all_at_once,   // All at once
  three_per,  // 3 at once random
  rvs         // Random in blocks of 5


Current duty cycle modes are...
  none, //run at 100% duty cycle always
  bounce, //Swap between given duty cycle and 100% repeatedly during given intervals.
  rand_pattern, //50% chance to swap every interval 
  constant //Always use given duty cycle 

*/
// ###########################################################################################################
// EDITABLE VARIABLES
// rvs or 
// ============================================================
const pattern_mode selected_mode = all_at_once;// Select this depending on chosen algorithm
//const pattern_mode selected_mode = rvs;          // Select this depending on chosen algorithm
//const pattern_mode selected_mode = all_off;          // Select this depending on chosen algorithm
const int num_motors = 5;// CHANGE THIS DEPENDING ON # OF MOTORS


// A0:A4 = 14:18
// all pins used: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}

// OUR GLOVES:
// small white left : {8,7,4,3,2};
// large black glove right : {14, 16, 18, 2, 6};
// large black glove left : {6, 2, 18, 16, 14};
// medium black glove right : {6, 2, 18, 16, 14};
// medium left white glove: {8, 7, 4, 3, 2};
// medium left pattern glove:  {14, 16, 18, 2, 6};
//int fingers[num_motors] =  {2,3,4,5,6};
//int fingers[num_motors] =  {14, 16, 18, 2, 6};  // left hand medium swirl glove
//int fingers[num_motors] = {6, 2, 18, 16, 14};     // right hand medium carat glove



int fingers[num_motors] =    {14, 16, 18, 2, 4};

//int fingers[num_motors] = {10, 5, 4, 3, 2};

// medium right pattern glove: 
// int fingers[num_motors] = {14, 16, 18, 2, 6};

// int fingers[num_motors] = {8, 7, 4, 3, 2} ; //For gloves motors are on pins A0, A2, A4, 2, and 6

const int delay_millis = 1000; //Delay time in milliseconds between changes in activated motor or vibrational intensity
const bool serialMon = true; //Weather to print to serial monitor or not

// VIBRATIONAL INTENSITY MANAGEMENT.
const float duty_cycle = 0.35; //Duty cycle (fraction of 1 between 0.2 and 1.0). Minimum of 0.3, max of 1. 0.35 ~ 1v ~ 70-100 hz
// Set to 0.4 for sleeves, 0.35 for gloves

//SET THIS FOR STRENGTH AND PATTERN:
// none = all high strength
// bounce = alternate between strong and weak each new stim
// rand_pattern = random strenth each time
// constant = always weak
const duty_cycle_mode cycle_mode = constant; //Select this depending on how duty cycle changes


// TIMER INFORMATION
bool timer_print = false; //Prints time stored on arduino to serial monitor
bool reset_time = false; //Resets the time on the arduino if true. Will lose all time information.
// ###########################################################################################################


PatternTracker worker = PatternTracker(fingers, num_motors, selected_mode, delay_millis, serialMon, duty_cycle, cycle_mode);

int cycle = 1; //Cycle 1
ISR(TIMER2_COMPA_vect){//timer2 interrupt for manual PWM
  if(worker.pwm) {
    if (cycle == 1){ //End Cycle 1, Start cycle 2
      worker.motorOff();
      OCR2A = worker.cycle2;
      cycle = 2;
    }
    else{ //End Cycle 2, Start cycle 1
      worker.motorOn();
      OCR2A = worker.cycle1;
      cycle = 1;
    }
  } else {
    worker.motorOn();
  }
}
  

void interruptTimerSetup() { //Sets up PWM timer. Uses Timer2
    cli();//stop interrupts
    //set timer2 interrupt 
    TCCR2A = 0;// set entire TCCR2A register to 0
    TCCR2B = 0;// same for TCCR2B
    TCNT2  = 0;//initialize counter value to 0
    // set compare match register for 
    OCR2A = worker.cycle1;
    // turn on CTC mode
    TCCR2A |= (1 << WGM21);
    // Set CS21 and CS20 bit for x1024 prescaler
    TCCR2B |= (1 << CS21) | (1 << CS20);
    // enable timer compare interrupt
    TIMSK2 |= (1 << OCIE2A);
    sei();//allow interrupts
}

//Timer Information
TimerTracker timerTracker;

void setup() {
  Serial.begin(9600); //This is for testing
  if(cycle_mode != none){
    interruptTimerSetup();
  }
  timerTracker.start();
  if(reset_time) {
    timerTracker.reset();
  }
}

void loop() {
  for(int i = 0; i<1000000; i++){

    worker.patternLoop();

    if (i == 0) {
      timerTracker.update();
      if (timer_print) {
        timerTracker.timePrint();
      }
    }
  }
}
