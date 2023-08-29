from collections import OrderedDict
import json
import requests
from flask import Flask, Response, render_template
import speedtest
import time
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)


def get_info(i):
    response = requests.get('https://ipinfo.io/json')
    data = json.loads(response.text)
    return data.get(i, "")

@app.route('/')
def home():
    return render_template('index.html')
def run_speed_test():
    st = speedtest.Speedtest()
    st.get_best_server()
    user_ip = requests.get("https://api.ipify.org").text

    download_speeds = []
    upload_speeds = []

    end_time = time.time() + 10  # Run the test for 15 seconds

    while time.time() < end_time:
        download_speed = st.download() / 1024 / 1024  # Convert to Mbps
        upload_speed = st.upload() / 1024 / 1024  # Convert to Mbps

        download_speeds.append(download_speed)
        upload_speeds.append(upload_speed)

        time.sleep(1)

    avg_download_speed = sum(download_speeds) / len(download_speeds)
    avg_upload_speed = sum(upload_speeds) / len(upload_speeds)

    speed_data = OrderedDict([
        ("download_speed", f"{round(avg_download_speed, 2)} Mbps"),
        ("upload_speed", f"{round(avg_upload_speed, 2)} Mbps"),
        ("ip", user_ip),
        ("network-org", get_info('org')),
        ("location", get_info('country') + ', ' + get_info('region') + ', ' + get_info('city')),
    ])

    if get_info('hostname'):
        speed_data["hostname"] = get_info('hostname')

    json_output = json.dumps(speed_data, indent=2)  # Convert OrderedDict to JSON string

    # Return the JSON string as a Response object with proper content type
    return Response(json_output, content_type="application/json")

@app.route('/json')
def start_speed_test():
    speed_data = run_speed_test()
    return speed_data

if __name__== '__main__':
    app.run()
