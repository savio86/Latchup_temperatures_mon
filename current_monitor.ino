
int Alert_3_3V_pin = 7;
int Alert_1_8V_pin = 6;

int Digital_Alert_3_3V_pin = 2;
int Digital_Alert_1_8V_pin = 3;

int Reset_3_3V_pin = 9;
int Reset_1_8V_pin = 8;


int LED_1_8V_pin = 4;
int LED_3_3V_pin = 5;

int Alert_3_3V;
int Alert_1_8V;
int Digital_Alert_3_3V;
int Digital_Alert_1_8V;
int Reset_3_3V;
int Reset_1_8V;
int LED_1_8V;
int LED_3_3V;

char incomingByte =-1;
int latchup_count_1_8 =0;
int latchup_count_3_3 =0;
int pressure =0;
int Current1=0;
int Current2=0;
int temp=0;

int temperature;

// the setup routine runs once when you press reset:
void setup() {
// initialize serial communication at 9600 bits per second:
  Serial.begin(9600);

  pinMode(Reset_3_3V_pin, OUTPUT);
  pinMode(Reset_1_8V_pin, OUTPUT);
  pinMode(Alert_3_3V_pin, INPUT);
  pinMode(Alert_1_8V_pin, INPUT);
  digitalWrite( Alert_3_3V_pin,  HIGH);
  digitalWrite( Alert_1_8V_pin,  HIGH); 
  pinMode(LED_1_8V_pin, OUTPUT);
  pinMode(LED_3_3V_pin, OUTPUT);
  pinMode(Digital_Alert_3_3V_pin, OUTPUT);
  pinMode(Digital_Alert_1_8V_pin, OUTPUT);
  digitalWrite(LED_3_3V_pin, LOW);
  digitalWrite(LED_1_8V_pin, LOW);
}
  
// the loop routine runs over and over again forever:
void loop() {

  
 digitalWrite( Digital_Alert_3_3V_pin, HIGH);
 digitalWrite( Digital_Alert_1_8V_pin, HIGH);
 digitalWrite( Reset_3_3V_pin, HIGH);
 digitalWrite( Reset_1_8V_pin,  HIGH);
 digitalWrite(LED_3_3V_pin, LOW);
 digitalWrite(LED_1_8V_pin, LOW);
 incomingByte =-1;
 Alert_3_3V=digitalRead(Alert_3_3V_pin);
 Alert_1_8V=digitalRead(Alert_1_8V_pin);
 
  
  if ((Alert_3_3V == LOW) or (Alert_1_8V == LOW)){           // if an overcurrent signal occurs
    
     digitalWrite( Digital_Alert_1_8V_pin, LOW);             //shut-down 1,8V power
     digitalWrite( Digital_Alert_3_3V_pin, LOW);             //shut-down 3,3V power

    if (Alert_3_3V == LOW){                                 //check if was an overcurrent on 3,3V power net
       latchup_count_3_3 ++;                                //increment the latch-up counter
       digitalWrite(LED_3_3V_pin, HIGH);                    //turn on the LED
     }
     else if(Alert_1_8V == LOW){                            //check if was an overcurrent on 1,8V power net
       latchup_count_1_8 ++;                                //increment the latch-up counter     
       digitalWrite(LED_1_8V_pin, HIGH);                    //turn on the LED
     }
     delay(1000);                                           //wait to recover from latch-up
     //Serial.print(latchup_count_1_8);                       //send the number of latch-up on the 1,8V 
    // Serial.print(latchup_count_3_3);                       //send the number of latch-up on the 3,3V 
     if (Serial.available() > 0){
       Serial.print('!');}
     digitalWrite( Reset_3_3V_pin, LOW);                    //reset the current monitor device
     digitalWrite( Reset_1_8V_pin,  LOW);                   //reset the current monitor device
     digitalWrite( Digital_Alert_1_8V_pin, HIGH);           //turn on the 1,8V power
     digitalWrite( Digital_Alert_3_3V_pin, HIGH);           //turn on the 3,3V power
     digitalWrite(LED_3_3V_pin, LOW);                       //turn off the LED
     digitalWrite(LED_1_8V_pin, LOW);                       //turn off the LED
  }
   
  
  if (Serial.available() > 0) {                           //if there is an incoming byte from the serial
    incomingByte = Serial.read();                         //store it in the incomingByte variable
  }   
  if (incomingByte != -1) {                             
    if (incomingByte == 't') {                            //if the incoming byte is "t"
        for (int i = 3; i<9; i++ ) {                      // read and send the temperatures
        temperature = analogRead(i);
      //  Serial.print("Sens. Value:");                   //uncomment this row for debug
      //  Serial.println(i-1);                            //uncomment this row for debug
        Serial.print(temperature);
        Serial.print(' ');
      }
      Serial.print('#');
    }
     else if (incomingByte == 'c') {                      //if the incoming byte is "c"
      //Serial.print("Current_1.8V: ");                   //uncomment this row for debug
      temp= analogRead(1);                                // read and send the current value on 1,8V  
      Serial.print(temp);
      Serial.print(' ');
      //Serial.println("A");                              //uncomment this row for debug
      //Serial.print("Current_3.3V: ");                   //uncomment this row for debug    
      temp= analogRead(0);                                // read and send the current value on 3,3V
      Serial.print(temp);
      //Serial.println("A");                              //uncomment this row for debug
     

     }
     else if (incomingByte == 'p') {                      //if the incoming byte is "p"
      //Serial.print("Pressure: ");                       //uncomment this row for debug
      pressure= analogRead(2);                            // read and send the pressure value
        Serial.print(pressure);                           //formula to be done on SW pressure= ADCread/9.21 +10.56;
      //Serial.println(" kPa");                           //uncomment this row for debug

    }
    else if (incomingByte == 'l'){                        //if the incoming byte is "l"  

      //Serial.print("Number of latchup on 1.8V: ");      //uncomment this row for debug
      Serial.print(latchup_count_1_8);                  //send the number of latch-up on the 1,8V 
      Serial.print(' ');
      //Serial.print("Number of latchup on 3.3V: ");      //uncomment this row for debug
      Serial.print(latchup_count_3_3);                  //send the number of latch-up on the 3,3V 
     

      
    }
  }
}
