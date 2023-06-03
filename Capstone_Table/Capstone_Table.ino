#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 nrf(9, 8);  // CE, CSN
const byte linkAddress[6] = "link1";  //address through which two modules communicate.
const byte greenLED = 10;
float data[2];
float prev_acceleration = 0;
float acceleration = -1;
float diff = 0;
float heading = -1;

// For SPI mode, we need a CS pin
#define ICM_CS 10
// For software-SPI mode we need SCK/MOSI/MISO pins
#define ICM_SCK 13
#define ICM_MISO 12
#define ICM_MOSI 11

void setup()
{ 
  Serial.begin(115200);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens
  pinMode(greenLED, OUTPUT);
 
  nrf.begin();    
  nrf.setPALevel(RF24_PA_LOW); //MIN, LOW, HIGH
  nrf.openReadingPipe(0, linkAddress);  //set the address 
  nrf.startListening();   //Set nrf as receiver
  Serial.println("Starting");
}
///////////////////////////////////////////////////
void loop()
{  
   if (nrf.available())  //Read the data if available in buffer
     {
      nrf.read(&data, sizeof(data));
      prev_acceleration = acceleration;
      acceleration = data[0];
      heading = data[4];
    }
    else {
    } 

    diff = prev_acceleration - acceleration; 
    
    if (diff >= 5) {
      Serial.println(prev_acceleration);
    }
    

    if (diff >= 10) {
      delay(10);
    }
    else {
      delay(10);
    }
}
//////////////////////////////////////////////