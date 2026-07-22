#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include "Bonezegei_DHT11.h"

const char* ssid = "MIST";
const char* password = "Il0veMIST";
const char* serverURL = "https://autonomousexplorer-production.up.railway.app/update";
#define ROBOT_ID "BOT-001"

#define MQ7_PIN  1     // ADC-capable pin on C6
#define MQ135_PIN 0    // ADC-capable pin on C6
#define DHT_PIN  4

#define WINDOW 20
#define CO_ABS_MAX 2800
#define AIR_ABS_MAX 2800
#define TEMP_ABS_MAX 50.0
#define HUM_ABS_MAX 95.0

Bonezegei_DHT11 dht(DHT_PIN);

float co_hist[WINDOW], air_hist[WINDOW], temp_hist[WINDOW], hum_hist[WINDOW];
int idx = 0;
bool historyFilled = false;

float mean(float* a, int n){ float s=0; for(int i=0;i<n;i++) s+=a[i]; return s/n; }
float stddev(float* a, int n, float m){ float s=0; for(int i=0;i<n;i++) s+=pow(a[i]-m,2); return sqrt(s/n); }
bool isAnomaly(float* h, float v){
  if (!historyFilled) return false;
  float m = mean(h, WINDOW), sd = stddev(h, WINDOW, m);
  if (sd < 0.01) return false;
  return abs((v - m) / sd) > 2.5;
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(300); Serial.print("."); }
  Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
}

void loop() {
  dht.getData();
  float t = dht.getTemperature();
  float h = dht.getHumidity();
  int co = analogRead(MQ7_PIN);
  int air = analogRead(MQ135_PIN);

  bool z_alert = isAnomaly(co_hist, co) || isAnomaly(air_hist, air)
               || isAnomaly(temp_hist, t) || isAnomaly(hum_hist, h);
  bool abs_alert = co > CO_ABS_MAX || air > AIR_ABS_MAX
                 || t > TEMP_ABS_MAX || h > HUM_ABS_MAX;
  bool danger = z_alert || abs_alert;

  co_hist[idx] = co; air_hist[idx] = air; temp_hist[idx] = t; hum_hist[idx] = h;
  idx = (idx + 1) % WINDOW;
  if (idx == 0) historyFilled = true;

  String msg = "ID:" ROBOT_ID
               ",CO:" + String(co) +
               ",AIR:" + String(air) +
               ",TEMP:" + String(t) +
               ",HUM:" + String(h) +
               ",STATUS:" + String(danger ? "DANGER" : "NORMAL");

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;
    http.begin(client, serverURL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    int code = http.POST("data=" + msg);
    Serial.println("Sent, response: " + String(code));
    http.end();
  }

  Serial.println(msg);
  delay(2000);
}