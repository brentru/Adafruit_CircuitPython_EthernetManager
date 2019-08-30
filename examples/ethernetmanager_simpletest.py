import board
import busio
import time
import neopixel

import socket
import adafruit_ethernetmanager as eth

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

# Initialize a new EthernetManager object
ethernet = eth.EthernetManager(spi, board.D10, status_pixel=status_light, debug=True)

print("Attempting to connect to ethernet...")
ethernet.connect()
print("Connected to with IP: ", ethernet.ip_address)

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_GET_URL = "http://httpbin.org/get"
JSON_POST_URL = "http://httpbin.org/post"

print("Fetching text from %s"%TEXT_URL)
response = ethernet.get(TEXT_URL)
print('-'*40)

print("Text Response: ", response.text)
print('-'*40)
response.close()

print("Fetching JSON data from %s"%JSON_GET_URL)
response = ethernet.get(JSON_GET_URL)
print('-'*40)

print("JSON Response: ", response.json())
print('-'*40)
response.close()

data = '31F'
print("POSTing data to {0}: {1}".format(JSON_POST_URL, data))
response = ethernet.post(JSON_POST_URL, data=data)
print('-'*40)

json_resp = response.json()
# Parse out the 'data' key from json_resp dict.
print("Data received from server:", json_resp['data'])
print('-'*40)
response.close()

json_data = {"Date" : "July 25, 2019"}
print("POSTing data to {0}: {1}".format(JSON_POST_URL, json_data))
response = ethernet.post(JSON_POST_URL, json=json_data)
print('-'*40)

json_resp = response.json()
# Parse out the 'json' key from json_resp dict.
print("JSON Data received from server:", json_resp['json'])
print('-'*40)
response.close()
