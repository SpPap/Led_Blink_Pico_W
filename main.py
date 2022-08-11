import time
import network
import machine
from secrets import secrets
from machine import Pin
import socket

onboard_led = machine.Pin('LED', machine.Pin.OUT)
led = machine.Pin(26, machine.Pin.OUT)
led_status = "OFF"

wlan = network.WLAN(network.STA_IF)

#Credentials
ssid = secrets['ssid']
password = secrets['password']

def blink_led(frequency = 0.5, num_blinks = 3):
    for _ in range(num_blinks):
        onboard_led.on()
        time.sleep(frequency)
        onboard_led.off()
        time.sleep(frequency)


def connect_to_wifi():
    wlan.active(True)
    wlan.config(pm = 0xa11140)  # Disable powersaving mode
    wlan.connect(ssid, password)

    # Wait for connect or fail (10s timeout)
    timeout = 10
    while timeout > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        timeout -= 1
        print('Waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        blink_led(0.1, 10)
        raise RuntimeError('WiFi connection failed')
    else:
        blink_led(0.5, 2)
        print('Connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

#Load html page
def get_html(html_name, led_status):
    with open(html_name, 'r') as file:
        html = file.read()

    return html.replace("$status", led_status)

print('Connecting to WiFi...')
connect_to_wifi()

#HTTP Server with socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s =  socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

# Listen for connections
while True:
    try:
        client_socket, addr = s.accept()
        print('Client connected from', addr)
        r = client_socket.recv(1024)
        #print(r)
        
        r = str(r)
        led_on = r.find('?led=on')
        led_off = r.find('?led=off')
        #print('led_on = ', led_on)
        #print('led_off = ', led_off)
        
        if led_on > -1:
            led_status = "ON"
            print('LED ON')
            led.value(1)
            
        if led_off > -1:
            led_status = "OFF"
            print('LED OFF')
            led.value(0)
            
        response = get_html('index.html', led_status)
        client_socket.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        client_socket.send(response)
        client_socket.close()
        
    except OSError as e:
        client_socket.close()
        print('Connection closed')


