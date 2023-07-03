/*
The Code which allows the cue stick to talk to the arduino on the pool table to
display the shot speed and direction
Author: Justin Rager
*/

#include <Adafruit_ICM20X.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <math.h>
//nrf2401 transmitter:
#include <SPI.h>
#include <RF24.h>
#include <nRF24L01.h>
RF24 nrf(9, 8);  // CE, CSN

const byte linkAddress[6] = "link1";
float data[2];

Adafruit_ICM20948 icm;
uint16_t measurement_delay_us = 65535; // Delay between measurements for testing
// For SPI mode, we need a CS pin
#define ICM_CS 10
// For software-SPI mode we need SCK/MOSI/MISO pins
#define ICM_SCK 13
#define ICM_MISO 12
#define ICM_MOSI 11

void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  // Try to initialize!
  if (!icm.begin_I2C()) {
    // if (!icm.begin_SPI(ICM_CS)) {
    // if (!icm.begin_SPI(ICM_CS, ICM_SCK, ICM_MISO, ICM_MOSI)) {

    Serial.println("Failed to find ICM20948 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("ICM20948 Found!");
  // icm.setAccelRange(ICM20948_ACCEL_RANGE_16_G);
  Serial.print("Accelerometer range set to: ");
  switch (icm.getAccelRange()) {
  case ICM20948_ACCEL_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case ICM20948_ACCEL_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case ICM20948_ACCEL_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case ICM20948_ACCEL_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  Serial.println("OK");

  // icm.setGyroRange(ICM20948_GYRO_RANGE_2000_DPS);
  Serial.print("Gyro range set to: ");
  switch (icm.getGyroRange()) {
  case ICM20948_GYRO_RANGE_250_DPS:
    Serial.println("250 degrees/s");
    break;
  case ICM20948_GYRO_RANGE_500_DPS:
    Serial.println("500 degrees/s");
    break;
  case ICM20948_GYRO_RANGE_1000_DPS:
    Serial.println("1000 degrees/s");
    break;
  case ICM20948_GYRO_RANGE_2000_DPS:
    Serial.println("2000 degrees/s");
    break;
  }

  //  icm.setAccelRateDivisor(4095);
  uint16_t accel_divisor = icm.getAccelRateDivisor();
  float accel_rate = 1125 / (1.0 + accel_divisor);

  Serial.print("Accelerometer data rate divisor set to: ");
  Serial.println(accel_divisor);
  Serial.print("Accelerometer data rate (Hz) is approximately: ");
  Serial.println(accel_rate);

  //  icm.setGyroRateDivisor(255);
  uint8_t gyro_divisor = icm.getGyroRateDivisor();
  float gyro_rate = 1100 / (1.0 + gyro_divisor);

  Serial.print("Gyro data rate divisor set to: ");
  Serial.println(gyro_divisor);
  Serial.print("Gyro data rate (Hz) is approximately: ");
  Serial.println(gyro_rate);

  // icm.setMagDataRate(AK09916_MAG_DATARATE_10_HZ);
  Serial.print("Magnetometer data rate set to: ");
  switch (icm.getMagDataRate()) {
  case AK09916_MAG_DATARATE_SHUTDOWN:
    Serial.println("Shutdown");
    break;
  case AK09916_MAG_DATARATE_SINGLE:
    Serial.println("Single/One shot");
    break;
  case AK09916_MAG_DATARATE_10_HZ:
    Serial.println("10 Hz");
    break;
  case AK09916_MAG_DATARATE_20_HZ:
    Serial.println("20 Hz");
    break;
  case AK09916_MAG_DATARATE_50_HZ:
    Serial.println("50 Hz");
    break;
  case AK09916_MAG_DATARATE_100_HZ:
    Serial.println("100 Hz");
    break;
  }
  Serial.println();

  Serial.println("BMP280/NRF24L01 link");
  nrf.begin();   
  nrf.openWritingPipe(linkAddress);  
  nrf.setPALevel(RF24_PA_LOW); //MIN, LOW, HIGH
  nrf.stopListening();  //act as a transmitter

  Serial.println("Setup Complete");

}

void loop() {
  static float acceleration = 0;

  static float magneticX = 0;
  static float magneticY = 0;
  static float magneticZ = 0;

  //  /* Get a new normalized sensor event */
  sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t mag;
  sensors_event_t temp;
  icm.getEvent(&accel, &gyro, &temp, &mag);

  static float calX = accel.acceleration.x;
  static float calY = accel.acceleration.y;
  static float calZ = accel.acceleration.z;

  accel.acceleration.x -= calX;
  accel.acceleration.y -= calY;
  accel.acceleration.z -= calZ;

  acceleration = sqrt(pow(accel.acceleration.x, 2) + pow(accel.acceleration.y, 2) + pow(accel.acceleration.z, 2));

  static float calMagX = mag.magnetic.x;
  static float calMagY = mag.magnetic.y;
  static float calMagZ = mag.magnetic.z;

  static float heading = 0; 

  //convert from uT to Gauss
  mag.magnetic.x /= 100;  
  mag.magnetic.y /= 100;
  mag.magnetic.z /= 100;

  heading = atan2(mag.magnetic.x, mag.magnetic.y);
  heading = heading * 180 / PI;
  if (heading < 0) {
    heading += 360;
  }
  if (heading > 360) {
    heading -= 360;
  }

  data[0] = acceleration;
  data[4] = heading;

  if (nrf.write(&data, sizeof(data))) {
    Serial.println("DATA SENT");
  }
  else {
    Serial.println("NO DATA");
  }

  
  Serial.print("Data: ");
  Serial.print(sizeof(data));
  Serial.print(" ");
  for(int i = 0; i < sizeof(data); i++)
  {
    Serial.print(data[i]);
    Serial.print(" ");
  }
  Serial.println();
  

  delay(50); // in ms
}
