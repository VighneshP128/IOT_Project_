import json
import time
import requests
import mysql.connector
import paho.mqtt.client as mqtt

# ---------- MQTT ----------
MQTT_BROKER = "10.153.97.8"
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/sensors"

# ---------- MySQL ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="iot_db"
)
cursor = db.cursor()

# ---------- ThingSpeak ----------
THINGSPEAK_API_KEY = "6FLG7IT5KY4IW1CC"
THINGSPEAK_URL = "https://api.thingspeak.com/update"
last_ts_update = 0   # timestamp

def on_message(client, userdata, msg):
    global last_ts_update

    try:
        data = json.loads(msg.payload.decode())
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        gas = int(data["gas"])

        print("Received:", data)

        # ----- MySQL -----
        cursor.execute(
            "INSERT INTO sensor_data (temperature, humidity, gas) VALUES (%s,%s,%s)",
            (temperature, humidity, gas)
        )
        db.commit()
        print("✔ MySQL updated")

        # ----- ThingSpeak (STRICT 15s RULE) -----
        if time.time() - last_ts_update >= 15:
            response = requests.post(
                THINGSPEAK_URL,
                data={
                    "api_key": THINGSPEAK_API_KEY,
                    "field1": temperature,
                    "field2": humidity,
                    "field3": gas
                },
                timeout=5
            )

            print("ThingSpeak raw response:", response.text)

            # SUCCESS only if response is NOT "0"
            if response.text.strip() != "0":
                print("✔ ThingSpeak updated successfully")
                last_ts_update = time.time()
            else:
                print("❌ ThingSpeak rejected (15s rule or API key)")

    except Exception as e:
        print("ERROR:", e)

# ---------- MQTT CLIENT ----------
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC)
client.on_message = on_message

print("MQTT → MySQL + ThingSpeak bridge running...")
client.loop_forever()