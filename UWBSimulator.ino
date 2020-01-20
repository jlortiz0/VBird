bool UWBEnabled;
bool rts;
String inBuffer = "";
float slope;
float yint;
float vel;
float z;
float x = 0;
float emuZ = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  while (!Serial) {}
}

void loop() {
  // put your main code here, to run repeatedly:
  while (Serial.available()) {
    inBuffer += (char)Serial.read();
    if (inBuffer.endsWith("\n")) {
      if (inBuffer == "reset\r\n") {
        UWBEnabled = false;
        rts = false;
        x = 0;
        emuZ = 0;
        Serial.println(F("jj"));
      } else if (inBuffer == "lep\n") {
        UWBEnabled = true;
        //Serial.print(F("POS,0,ABCD,0,0,"));
        //Serial.println(emuZ);
      } else if (inBuffer.startsWith("in ")) {
        Serial.print(inBuffer);
        inBuffer.remove(0,3);
        slope = inBuffer.substring(0, inBuffer.indexOf(' ')).toFloat();
        inBuffer.remove(0, inBuffer.indexOf(' ')+1);
        yint = inBuffer.substring(0, inBuffer.indexOf(' ')).toFloat();
        inBuffer.remove(0, inBuffer.indexOf(' ')+1);
        vel = inBuffer.substring(0, inBuffer.indexOf(' ')).toFloat()/8;
        inBuffer.remove(0, inBuffer.indexOf(' ')+1);
        z = inBuffer.substring(0, inBuffer.indexOf(' ')).toFloat();
        rts = true;
      }
      inBuffer = "";
    }
  }
  if (UWBEnabled && rts) {
    if (z != emuZ) {
      if (abs(z-emuZ) < 0.1) {
        emuZ = z;
      } else if (z > emuZ) {
        emuZ += 0.125;
      } else if (z < emuZ) {
        emuZ -= 0.125;
      }
    } else {
      x += vel;
    }
    Serial.print(F("POS,0,ABCD,"));
    Serial.print(x);
    Serial.print(F(","));
    Serial.print(x*slope + yint);
    Serial.print(F(","));
    Serial.println(emuZ);
  }
  delay(125);
}
