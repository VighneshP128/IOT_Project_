from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="iot_db",
        autocommit=True
    )

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/data")
def data():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT temperature, humidity, gas, created_at
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(rows[::-1])  # oldest → newest

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)