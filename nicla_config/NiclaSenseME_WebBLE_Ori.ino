/*

Arduino Nicla Sense ME WEB BLE Sense dashboard demo


Hardware required: https://store.arduino.cc/nicla-sense-me

1) Upload this sketch to the Arduino Nano BLE sense board

2) Open the following web page in the Chrome browser:
https://arduino.github.io/ArduinoAI/NiclaSenseME-dashboard/

3) Click on the green button in the web page to connect the browser to the board over BLE


Web dashboard by D. Pajak

Device sketch based on example by Sandeep Mistry and Massimo Banzi
Sketch and web dashboard copy-fixed to be used with the Nicla Sense ME by Pablo Marquínez

*/

#include "Nicla_System.h"
#include "Arduino_BHY2.h"
#include <ArduinoBLE.h>

#define BLE_SENSE_UUID(val) ("19b10000-" val "-537e-4f6c-d104768a1214")

const int VERSION = 0x00000000;

BLEService service(BLE_SENSE_UUID("0000"));

BLECharacteristic orientationCharacteristic(BLE_SENSE_UUID("1001"), BLERead | BLENotify, 3 * sizeof(int16_t)); // Array of 3x 2 Bytes, XYZ

// String to calculate the local and device name
String name;

SensorOrientation orientation(SENSOR_ID_ORI);


void setup(){
  Serial.begin(115200); 

  Serial.println("Start");

  nicla::begin();
  nicla::leds.begin();
  nicla::leds.setColor(green);

  //Sensors initialization
  BHY2.begin(NICLA_STANDALONE);

  orientation.begin(10,1);

  if (!BLE.begin()){
    Serial.println("Failled to initialized BLE!");

    while (1)
      ;
  }

  String address = BLE.address();

  Serial.print("address = ");
  Serial.println(address);

  address.toUpperCase();

  name = "NiclaSenseME-";
  name += address[address.length() - 5];
  name += address[address.length() - 4];
  name += address[address.length() - 2];
  name += address[address.length() - 1];

  Serial.print("name = ");
  Serial.println(name);

  BLE.setLocalName(name.c_str());
  BLE.setDeviceName(name.c_str());
  BLE.setAdvertisedService(service);

  // Add all the previously defined Characteristics
  service.addCharacteristic(orientationCharacteristic);

  BLE.addService(service);
  BLE.advertise();
}

void loop(){
  while (BLE.connected()){
    BHY2.update(100);
    
    if(orientationCharacteristic.subscribed()){
      float x,y,z;
      
      x = orientation.pitch();
      y = orientation.roll();
      z = orientation.heading();
      
      int16_t oriValues[3] = {x,y,z};
      orientationCharacteristic.writeValue(oriValues, sizeof(oriValues));
    }
  }
}