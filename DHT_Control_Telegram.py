import machine
import network
import time
import urequests
import dht

gc.collect()
dht_pin = machine.Pin(15)
d = dht.DHT11(dht_pin)
HTTP_HEADERS = {'Content-Type' : 'application/json'}
TOKEN = "6344715372:AAHS6LXDVRUohW9W2VZVolwhnI-CZ_bFXCM" 
chat_id = "1183840606"
message_id_prev = "0"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
def connect_wifi(ssid, password, timeout=10):
    wlan.connect(ssid, password)
    print("Connecting to network...")
    start_time = time.ticks_ms()
    while not wlan.isconnected() and (time.ticks_ms() - start_time < timeout * 1000):
        time.sleep(1)
    if wlan.isconnected():
        print("Connected to network:", wlan.ifconfig()[0])
    else:
        print("Connection failed!")
        machine.reset()

def send_message(message):
    try:
        url = "https://api.telegram.org/bot{}/sendMessage".format(TOKEN)
        data = {
            "chat_id": chat_id,
            "text": message
        }
        response = urequests.post(url, json=data)
        response.close()

        if response.status_code == 200:
            json_data = response.json()
            print(json_data)
        else:
            print("Telegram API request failed with status code:", response.status_code)

    except Exception as e:
        print("Error while sending message:", str(e))

def check():
    global message_id_prev 
    response = urequests.get("https://api.telegram.org/bot{}/getUpdates".format(TOKEN))
    messages = response.json().get("result", [])
    response.close()
    latest_message = messages[-1]
    message_id_new = latest_message.get("update_id", "")
    text = latest_message.get("message", {}).get("text", "")
    print(text)
    print(message_id_new)
    print(message_id_prev)
    if(message_id_prev != message_id_new):
        d.measure()
        t = d.temperature()
        h = d.humidity()
        dht_readings = {"Temp": t, "Humidity": h}
            
        request = urequests.post(
                "https://api.thingspeak.com/update?api_key=" + "6B5UP2KHX6NISDZP",
                json=dht_readings,
                headers=HTTP_HEADERS,
        )
        request.close()
        print(f"Temperature: {t}°C, Humidity: {h}%" )
        mes = f"Temperature: {t}°C, Humidity: {h}%"            
        if text == "/send":
            send_message(mes)
            
        elif text == "/link":
            send_message("https://api.thingspeak.com/channels/2240065/charts/1")
        else :
            send_message("Invalid Command")
        message_id_prev = message_id_new
    else:
        print("Same message_id")

def main():
    connect_wifi("Udit Bansal", "p6vmut5b")

    while True:
        check()
        time.sleep(1)

if __name__ == "__main__":
    main()

