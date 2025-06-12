#include <Servo.h>
#include <PID_v1.h>  
// Definición de Servos
Servo servohori;
Servo servoverti; 
int servoh = 90;    // Posición inicial horizontal
int servov = 90;    // Posición inicial vertical
const int servohLimitHigh = 180;
const int servohLimitLow = 0;
const int servovLimitHigh = 180;
const int servovLimitLow = 0;

// Variables PID
double SetpointH = 0, InputH = 0, OutputH = 0;
double SetpointV = 0, InputV = 0, OutputV = 0;

// Ajustes PID 
double Kp = 0.8, Ki = 0.05, Kd = 0.1;
PID pidH(&InputH, &OutputH, &SetpointH, Kp, Ki, Kd, DIRECT);
PID pidV(&InputV, &OutputV, &SetpointV, Kp, Ki, Kd, DIRECT);

// Configuración
const int deadzone = 30;
float servoh_f = 90.0;
float servov_f = 90.0;

// Asignando LDRs
const int ldrtopl = A2; // Arriba Izquierda
const int ldrtopr = A1; // Arriba Derecha
const int ldrbotl = A3; // Abajo Izquierda
const int ldrbotr = A0; // Abajo Derecha

// Filtrado
const int numReadings = 3;
int readingsTopL[numReadings], readingsTopR[numReadings], readingsBotL[numReadings], readingsBotR[numReadings];
int readIndex = 0;
int totalTopL = 0, totalTopR = 0, totalBotL = 0, totalBotR = 0;

// Variables para gráficos
unsigned long previousMillis = 0;
const long interval = 200;

void setup() {
  servohori.attach(10);
  servoverti.attach(9);
  servohori.write(servoh);
  servoverti.write(servov);
  
  // Inicialización del filtro
  for (int i = 0; i < numReadings; i++) {
    readingsTopL[i] = readingsTopR[i] = readingsBotL[i] = readingsBotR[i] = 0;
  }
  
  // Configuración PID
  pidH.SetMode(AUTOMATIC);
  pidH.SetOutputLimits(-50, 50);  
  pidH.SetSampleTime(10);         
  
  pidV.SetMode(AUTOMATIC);
  pidV.SetOutputLimits(-50, 50);
  pidV.SetSampleTime(10);
  
  Serial.begin(115200);
  Serial.println("Horizontal,Vertical,TopL,TopR,BotL,BotR");
  delay(500);
}

void loop() {
  totalTopL -= readingsTopL[readIndex];
  readingsTopL[readIndex] = analogRead(ldrtopl);
  totalTopL += readingsTopL[readIndex];
  
  totalTopR -= readingsTopR[readIndex];
  readingsTopR[readIndex] = analogRead(ldrtopr);
  totalTopR += readingsTopR[readIndex];
  
  totalBotL -= readingsBotL[readIndex];
  readingsBotL[readIndex] = analogRead(ldrbotl);
  totalBotL += readingsBotL[readIndex];
  
  totalBotR -= readingsBotR[readIndex];
  readingsBotR[readIndex] = analogRead(ldrbotr);
  totalBotR += readingsBotR[readIndex];
  
  readIndex = (readIndex + 1) % numReadings;
  
  // Cálculos
  int avgtop = (totalTopL + totalTopR) / (2 * numReadings);
  int avgbot = (totalBotL + totalBotR) / (2 * numReadings);
  int avgleft = (totalTopL + totalBotL) / (2 * numReadings);
  int avgright = (totalTopR + totalBotR) / (2 * numReadings);

  // Entradas para los PID (diferencia de luz)
  InputV = avgbot - avgtop;  // Diferencia vertical
  InputH = avgleft - avgright; // Diferencia horizontal
  
  // Calcular salidas PID
  pidH.Compute();
  pidV.Compute();
  
  // Aplicar movimiento solo si estamos fuera de la zona muerta
  if (abs(InputV) > deadzone) {
    servov_f += OutputV * 0.1;  // Escalar la salida del PID
    servov_f = constrain(servov_f, servovLimitLow, servovLimitHigh);
    servov = round(servov_f);
  }
  
  if (abs(InputH) > deadzone) {
    servoh_f += OutputH * 0.1;  // Escalar la salida del PID
    servoh_f = constrain(servoh_f, servohLimitLow, servohLimitHigh);
    servoh = round(servoh_f);
  }
  
  // Movimiento de servos
  servoverti.write(servov);
  servohori.write(servoh);

  // Envío serial
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    Serial.print(servoh);
    Serial.print(',');
    Serial.print(servov);
    Serial.print(',');
    Serial.print(totalTopL/numReadings);
    Serial.print(',');
    Serial.print(totalTopR/numReadings);
    Serial.print(',');
    Serial.print(totalBotL/numReadings);
    Serial.print(',');
    Serial.println(totalBotR/numReadings);
  }

  delay(10);
}