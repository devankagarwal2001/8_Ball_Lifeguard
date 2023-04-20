#include <Servo.h>

const int buttonPin1 = 2;  // the number of the pushbutton pin
const int buttonPin2 = 4;  // the number of the pushbutton pin
const int ledPin = 13;    // the number of the LED pin
Servo myservo;  // create servo object to control a servo

// variables will change:
int buttonState1 = 0;  // variable for reading the pushbutton status
int buttonState2 = 0;  // variable for reading the pushbutton status
const int base = 0;    
int pos = 0;
const int angleChange = 130;

void setup() {
  // initialize the LED pin as an output:
  Serial.begin(115200);
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin1, INPUT);
  pinMode(buttonPin2, INPUT);
  myservo.attach(9);
}

void loop() {
  pos = 0;
  // read the state of the pushbutton value:
  buttonState1 = digitalRead(buttonPin1);
  buttonState2 = digitalRead(buttonPin2);
  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState1 == HIGH) {
    // turn LED on:
    //Serial.println("Green Button Pressed");
    pos = angleChange;
    myservo.write(pos); 
    delay(1500);
    pos = base;
    myservo.write(pos); 
    delay(1500);
  }
  if (buttonState2 == HIGH) {
    // turn LED on:
    //Serial.println("Red Button Pressed");
    pos = angleChange;
    myservo.write(pos); 
    delay(1500);
    pos = base;
    myservo.write(pos); 
    delay(1500);
  }  
}