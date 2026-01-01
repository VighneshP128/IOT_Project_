#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

/* ---------- WiFi ---------- */
const char* ssid = "vivo Y29 5G";
const char* password = "vanee2823";

/* ---------- Local MQTT ---------- */
const char* mqtt_server = " 10.185.217.127";
const int mqtt_port = 1883;
const char* mqtt_topic = "esp32/sensors";

/* ---------- Sensors ---------- */
#define DHTPIN 4
#define DHTTYPE DHT11
#define MQ2_PIN 34

DHT dht(DHTPIN, DHTTYPE);

/* ---------- MQTT ---------- */
WiFiClient espClient;
PubSubClient client(espClient);

/* ---------- WiFi ---------- */
void setupWiFi() {
  Serial.print("Connecting WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

/* ---------- MQTT ---------- */
void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting MQTT...");
    if (client.connect("ESP32_Client_01")) {
      Serial.println("Connected");
    } else {
      Serial.print("Failed rc=");
      Serial.print(client.state());
      Serial.println(" retry in 5s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setupWiFi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) reconnectMQTT();
  client.loop();

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int gas = analogRead(MQ2_PIN);

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Sensor error");
    delay(2000);
    return;
  }

  Serial.print("T:");
  Serial.print(temperature);
  Serial.print(" H:");
  Serial.print(humidity);
  Serial.print(" G:");
  Serial.println(gas);

  String payload = "{";
  payload += "\"temperature\":" + String(temperature) + ",";
  payload += "\"humidity\":" + String(humidity) + ",";
  payload += "\"gas\":" + String(gas);
  payload += "}";

  client.publish(mqtt_topic, payload.c_str());
  Serial.println("MQTT Published");

  delay(5000);   // ESP32 publish interval
}