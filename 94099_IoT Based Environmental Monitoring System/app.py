from flask import Flask, render_template, jsonify, make_response
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

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/data")
def data():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, temperature, humidity, gas
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 20
        """)

        rows = cursor.fetchall()
        cursor.close()
        db.close()

        rows.reverse()
        return make_response(jsonify(rows), 200)

    except Exception as e:
        print("ERROR:", e)
        return make_response(jsonify([]), 500)

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)