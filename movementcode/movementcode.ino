#include <Arduino.h>
#include <NewPing.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiClientSecure.h>
#include <ESP8266HTTPClient.h>

// ── WIFI ──
const char* ssid = "MIST";
const char* password = "Il0veMIST";
const char* serverURL = "https://autonomousexplorer-production.up.railway.app/update";
#define ROBOT_ID "BOT-001"

ESP8266WebServer server(80);

// ── MOTOR PINS ──
const int R1PWM = D1;
const int R2PWM = D2;
const int L1PWM = D3;
const int L2PWM = D4;

// ── ULTRASONIC PINS (shared TRIG, separate ECHO) ──
#define TRIG_PIN D0
#define ECHO_F   D5
#define ECHO_L   D6
#define ECHO_R   D7
#define ECHO_B   D8

#define MAX_DISTANCE 400
const int threshold = 80;

NewPing sonarF(TRIG_PIN, ECHO_F, MAX_DISTANCE);
NewPing sonarL(TRIG_PIN, ECHO_L, MAX_DISTANCE);
NewPing sonarR(TRIG_PIN, ECHO_R, MAX_DISTANCE);
NewPing sonarB(TRIG_PIN, ECHO_B, MAX_DISTANCE);

bool autoMode = true;
unsigned long lastManualCmd = 0;
const unsigned long manualTimeout = 1500;
unsigned long lastReport = 0;
String currentAction = "IDLE";

/* --- Motor Control --- */
void stopMotors() {
  analogWrite(R1PWM, 0); analogWrite(R2PWM, 0);
  analogWrite(L1PWM, 0); analogWrite(L2PWM, 0);
  currentAction = "STOP";
}
void moveForward(int speed) {
  analogWrite(R1PWM, speed); analogWrite(R2PWM, 0);
  analogWrite(L1PWM, speed); analogWrite(L2PWM, 0);
  currentAction = "FORWARD";
}
void moveBackward(int speed) {
  analogWrite(R1PWM, 0); analogWrite(R2PWM, speed);
  analogWrite(L1PWM, 0); analogWrite(L2PWM, speed);
  currentAction = "BACKWARD";
}
void turnRight(int speed) {
  analogWrite(R1PWM, 0); analogWrite(R2PWM, speed);
  analogWrite(L1PWM, speed); analogWrite(L2PWM, 0);
  currentAction = "TURN_RIGHT";
}
void turnLeft(int speed) {
  analogWrite(R1PWM, speed); analogWrite(R2PWM, 0);
  analogWrite(L1PWM, 0); analogWrite(L2PWM, speed);
  currentAction = "TURN_LEFT";
}

/* --- Web Handlers --- */
void handleRoot() {
  server.send(200, "text/html",
    "<h3>Bot Control</h3>"
    "<a href='/mode?m=auto'>AUTO</a> | <a href='/mode?m=manual'>MANUAL</a><br><br>"
    "<a href='/cmd?d=F'>Forward</a> "
    "<a href='/cmd?d=B'>Backward</a> "
    "<a href='/cmd?d=L'>Left</a> "
    "<a href='/cmd?d=R'>Right</a> "
    "<a href='/cmd?d=S'>Stop</a>");
}
void handleMode() {
  autoMode = (server.arg("m") == "auto");
  stopMotors();
  server.send(200, "text/plain", autoMode ? "AUTO" : "MANUAL");
}
void handleCmd() {
  if (autoMode) { server.send(200, "text/plain", "Switch to MANUAL first"); return; }
  String d = server.arg("d");
  lastManualCmd = millis();
  if (d == "F") moveForward(150);
  else if (d == "B") moveBackward(150);
  else if (d == "L") turnLeft(150);
  else if (d == "R") turnRight(150);
  else stopMotors();
  server.send(200, "text/plain", "OK");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(R1PWM, OUTPUT); pinMode(R2PWM, OUTPUT);
  pinMode(L1PWM, OUTPUT); pinMode(L2PWM, OUTPUT);
  stopMotors();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(300); Serial.print("."); }
  Serial.println("\nConnected! IP: " + WiFi.localIP().toString());

  server.on("/", handleRoot);
  server.on("/mode", handleMode);
  server.on("/cmd", handleCmd);
  server.begin();
}

void reportToDashboard(int distF, int distL, int distR, int distB) {
  if (WiFi.status() != WL_CONNECTED) return;

  String msg = "ID:" ROBOT_ID
               ",DISTF:" + String(distF) +
               ",DISTL:" + String(distL) +
               ",DISTR:" + String(distR) +
               ",DISTB:" + String(distB) +
               ",MOVE:" + currentAction +
               ",STATUS:NORMAL";

  WiFiClientSecure client;
  client.setInsecure();
  HTTPClient http;
  http.begin(client, serverURL);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  int code = http.POST("data=" + msg);
  http.end();
  Serial.println("Reported: " + msg + " | code:" + String(code));
}

void autonomousStep() {
  int distF = sonarF.ping_cm(); delay(30);
  int distL = sonarL.ping_cm(); delay(30);
  int distR = sonarR.ping_cm(); delay(30);
  int distB = sonarB.ping_cm(); delay(30);

  if (distF == 0) distF = MAX_DISTANCE;
  if (distL == 0) distL = MAX_DISTANCE;
  if (distR == 0) distR = MAX_DISTANCE;
  if (distB == 0) distB = MAX_DISTANCE;

  if (distF < threshold || distB < threshold) {
    stopMotors(); delay(200);
    if (distL > distR) turnLeft(150); else turnRight(150);
    delay(500);
  }
  else if (distL < 50) { turnRight(150); delay(100); }
  else if (distR < 50) { turnLeft(150);  delay(100); }
  else if (distB > 50) { moveBackward(70); }
  else { moveForward(70); }

  if (millis() - lastReport > 2000) {
    reportToDashboard(distF, distL, distR, distB);
    lastReport = millis();
  }
}

void loop() {
  server.handleClient();

  if (autoMode) {
    autonomousStep();
  } else if (millis() - lastManualCmd > manualTimeout) {
    stopMotors();
  }
}