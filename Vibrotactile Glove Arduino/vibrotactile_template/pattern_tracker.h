/*
  Functions made to read and preform motor functions based on a pattern given in RVS VR in a .txt
  Created by Brody SKaufel, July 13th, 2023
  Edited July 14th 2023 to use pointers
  Tested July 21st 2023 to bring to functional state in tests w/ glove
  Edited Nov 10 2023 to use Timer2 for manual PWM
*/
#ifndef pattern_tracker_h
#define pattern_tracker_h

#include <Arduino.h>

// ##################################################
    // Add enum for each new mode
enum pattern_mode
{
  in_order,     //tested w glove
  one_per,      //tested w glove
  all_at_once,  //tested w glove
  three_per,    //tested w glove
  rvs,           //tested w glove
  all_off
};

enum duty_cycle_mode
{
  none, //run at 100% duty cycle always
  bounce, //Swap between given duty cycle and 100% repeatedly during given intervals
  rand_pattern, //50% chance to swap every interval
  constant //Always use given duty cycle
};

class PatternTracker {
private:
// Use this to track which pins the motors are attatched to.]
  int* motor_pins_ptr;
  bool* motors_active_ptr;
  int num_motors;
  pattern_mode current_mode;
  int time_delay = 500;//in milliseconds
  bool print_true = false; //Set to true if want to print to serial monitor

  //Duty cycle
  float duty_cycle;
  duty_cycle_mode pwm_mode;

  //Tracks the last time an event took place
  unsigned long last_event_time = 0;
  //Used to prevent on the fly space assigning. Tracks current time in a variable used for Serial.
  unsigned long current_time = 0; 
  //True when vibrations are currently happening
  bool active_event = false;
  bool event_change = false;

  //These data structures are for any algorithms that need to reference future/past plans
  // For their operation, such as RVS
  int* planned_index; //Stores up to 2x # motors events, not all algo's use them
  int current_plan_index = 0;


  /* ##################################################
     Add function if adding new mode (define in .cpp)
     All these functions should do is set the array of finger_active to which
     fingers should be active
    */
  void run_one_per();
  void run_all_at_once();
  void run_three_per();
  void run_rvs();
  void run_in_order();

  //Other functions
  void shuffleArray(int * array, int size);
  void print();

public:
  int cycle1;
  int cycle2;
  bool pwm = true;
  void motorOn();
  void motorOff(); //Need to be here for ISR


  void patternLoop(); //For arduino loop

  PatternTracker(); //Default constructor

  // CLASS CONSTRUCTOR
  // motor_pins = array of pin # the motors are attatched to. 
  //    For hand, assumes index 0 is thumb
  //    for arm, no assumptions are made
  // num_motors = the number of motors/size of array
  // set_mode = algorithm that determines which finger activates
  // delay = Time in milliseconds an 'event' occurs for
  // Duty cycle = Specicied duty cycle of motor pins
  // pwm_mode = How to handle duty cycle
  PatternTracker(int *motor_pins, int num_motors, pattern_mode set_mode, int delay, bool reporting, float duty_cycle, duty_cycle_mode pwm_mode) {
    cycle1 = int(255*duty_cycle);
    cycle2 = 255 - cycle1; //We use 2 compare match interrupts.
    this->pwm_mode = pwm_mode;
    motor_pins_ptr = motor_pins;
    current_mode = set_mode;
    time_delay = delay;
    this->num_motors = num_motors;
    bool* false_array = new bool[num_motors];
    for(int i = 0; i < num_motors;++i) {
      false_array[i] = false;
    }
    motors_active_ptr = false_array;
    int* history = new int[num_motors*2];
    planned_index = history;

    //Sets pinmode
    for(int i = 0; i<num_motors; i++) {
      pinMode(motor_pins_ptr[i], OUTPUT);
    }
    print_true = reporting;
  }
  //Destructor
  ~PatternTracker() {
  delete[] motors_active_ptr;
  delete[] motor_pins_ptr;
  delete[] planned_index;
}
};

#endif
