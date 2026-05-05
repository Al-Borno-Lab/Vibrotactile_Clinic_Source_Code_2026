#include "pattern_tracker.h"

void PatternTracker::patternLoop(){
  if(active_event){
    if((last_event_time < millis()) && ((millis() - last_event_time) >= (time_delay))) {
      //Unsigned longs can't be negative. Means extra check.
      //There IS an active event and time delay has ended
      //Time to turn off
      for(int i = 0; i < num_motors; ++i){
        motors_active_ptr[i] = false;
      }
      active_event = false;
    }
  }
  if(!active_event) {
    // ##################################################
    // Add case if adding new mode
    switch(current_mode) {
      case one_per:
        run_one_per();
        break;
      case all_at_once:
        run_all_at_once();
        break;
      case three_per:
        run_three_per();
        break;
      case rvs:
        run_rvs();
        break;
      case in_order:
        run_in_order();
        break;
      default:
        if(print_true){
          Serial.println("ERROR");
        }
    }
    event_change = true; //A new change might have occured
    active_event = true;
    last_event_time = last_event_time  + time_delay; //Makes next goal for event
    switch(pwm_mode){
      case none:
        pwm = false;
        break;
      case bounce:
        pwm = !pwm;
        break;
      case rand_pattern:
        pwm = random(0, 2); //Picks between true and false
        break;
      case constant:
        pwm = true;
        break;
    }
  }

  if(event_change) {
    event_change = false;
    motorOn();
    if(print_true) {print();}
  }
}

void PatternTracker::motorOn(){
  for(int i = 0; i < num_motors; i++){
      if(motors_active_ptr[i]) {
        digitalWrite(motor_pins_ptr[i], HIGH);
      } else{
        digitalWrite(motor_pins_ptr[i], LOW);
      }
    }
}

void PatternTracker::motorOff(){
  for(int i = 0; i < num_motors; i++){
      digitalWrite(motor_pins_ptr[i], LOW);
    }
}

void PatternTracker::print() {
  current_time = millis();
  Serial.print("Time (Milliseconds): ");
  Serial.print(current_time);
  Serial.print(" ; Pins Array: ");
  for(int i = 0; i < num_motors; ++i){ //PRINTS OUT T/F ARRAY
    if(motors_active_ptr[i]) {
      Serial.print("T ");
    } else{
      Serial.print("F ");
    }
  }
  Serial.print("; Activated_Pins(int): ");
  for(int i = 0; i < num_motors; ++i){ //Prints out which pins were activated
    if(motors_active_ptr[i]) {
      Serial.print(motor_pins_ptr[i]);
      Serial.print(" ");
    }
  }
  Serial.println();
}

//A single, random motor
void PatternTracker::run_one_per() {
    int to_stim = random(5);
    motors_active_ptr[to_stim] = true;
}

//All motors at once
void PatternTracker::run_all_at_once() {
    for(int i = 0; i < num_motors; ++i){
      motors_active_ptr[i] = true;
    }
}

//Three random motors at once
void PatternTracker::run_three_per() {
    int gen_num = random((num_motors)*(num_motors-1)*(num_motors*2));
    int active1 = gen_num%(num_motors);
    int active2 = gen_num%(num_motors-1);
    int active3 = gen_num%(num_motors-2);
    if(active1<=active2) {
      active2++;
    }
    //The following corrects it
    if(active1<=active2) {
      active2++;
    }
    if(active1<=active3) {
      active3++;
    }
    if(active2<=active3) {
      active3++;
    }
    motors_active_ptr[active1] = true;
    motors_active_ptr[active2] = true;
    motors_active_ptr[active3] = true;
}

void PatternTracker::shuffleArray(int * array, int size)
{
  int last = 0;
  int temp = array[last];
  for (int i=0; i<size; i++)
  {
    int index = random(size);
    array[last] = array[index];
    last = index;
  }
  array[last] = temp;
}

//Each motor goes at least once per "block"
void PatternTracker::run_rvs() {
  if(current_plan_index == 0){
    //Set plan to follow

    int* plan = new int[num_motors];
    for(int i = 0; i < num_motors; i++){
      plan[i] = i;
    }
    shuffleArray(plan, num_motors);//This should shuffle the plan
    planned_index = plan;
    delete [] plan; //Stop memory leak
  } 

  int motor_index = planned_index[current_plan_index];
  motors_active_ptr[motor_index] = true;
  current_plan_index++;
  if(current_plan_index == num_motors) {
    current_plan_index = 0; //Reset block
  }
}

//All motors in order
void PatternTracker::run_in_order() {
  motors_active_ptr[current_plan_index] = true;
  current_plan_index++;
  if(current_plan_index==num_motors){
    current_plan_index = 0;//reset
  }
}
