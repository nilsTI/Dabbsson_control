# checkDBS2300 Example
# -*- coding: utf-8 -*-
"""
 Example script to monitor and control the state of a Dabbson BS2300 device.

 Author: nilsTI

 Using code from:
 https://github.com/jasonacox/tinytuya/blob/master/examples

"""

import http.server
import json
from urllib.parse import urlparse, parse_qs
import tinytuya
import time
from datetime import datetime
import logging
import traceback
import threading
import time
import base64
import struct

import credentials

s_t = datetime.now()                             
logging.basicConfig(filename=credentials.base_path+"log"+str(s_t.year)+"_"+str(s_t.month)+"_"+str(s_t.day)+"_"+str(s_t.hour)+"_"+str(s_t.minute)+"_"+str(s_t.second)+".txt", level=logging.INFO,format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logging.info(str('Start'))

status_json = {
    "timestamp": 0,
    "battery_1_load": 0,
    "battery_2_load": 0,
    "battery_1_temp": 0,
    "battery_2_temp": 0,
    "battery_1_solar_input": 0,
    "battery_2_input": 0,
    "battery_1_output": 0,
    "battery_2_output": 0,
    "ac_on": False,
    "dc_on": False,
    "v12_on": False
}

sendAcCmd = False

class DbsHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global status_json

        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status_json).encode('utf-8'))
        elif self.path == '/set':
            global sendAcCmd
            sendAcCmd = True
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status_json).encode('utf-8'))
        else:
            self.send_error(404, "File not found.")

    
timestamp = ""
battery_1_load = ""
battery_2_load = ""
battery_1_temp = ""
battery_2_temp = ""
battery_1_solar_input = ""
battery_2_input = ""
battery_1_output = ""
battery_2_output = ""
ac_on = ""
dc_on = ""
v12_on = ""

def parse_data(data):
    i = 0
    results = []
    while i < len(data):
        if i + 5 > len(data):
            break
        type_id = data[i]
        value = struct.unpack('>i', data[i + 1:i + 5])[0]
        results.append((type_id, value))
        i += 5
    return results

"""
Data examples:

{'protocol': 4, 't': 63848, 'data': {'dps': {'156': 'zQAAAADOAAAAANAAAAAA0QAAAADcExwhAN0AAAAB3gAAABs='}}, 'dps': {'156': 'zQAAAADOAAAAANAAAAAA0QAAAADcExwhAN0AAAAB3gAAABs='}}

{'protocol': 4, 't': 63848, 'data': {'dps': {'1': 9, '2': 4761, '10': 19, '103': 0, '104': 0, '105': 0, '106': 0, '110': 0, '108': 0, '138': 25, '139': 0}}, 'dps': {'1': 9, '2': 4761, '10': 19, '103': 0, '104': 0, '105': 0, '106': 0, '110': 0, '108': 0, '138': 25, '139': 0}}

"""
def process_payload(payload):
    global status_json

    global timestamp                # t
    global battery_1_load           # 1
    global battery_2_load           # 138
    global battery_1_temp           # 10
    global battery_2_temp           # in 156 -> 222?
    global battery_1_solar_input    # 103
    global battery_2_input          # in '156' -> 205
    global battery_1_output         # 108
    global battery_2_output         # 105 or in '156' -> 206

    global ac_on                    # 109
    global dc_on                    # 112
    global v12_on                   # 111

    extracted_data_time = payload.get('t')
    extracted_data_bat_1 = payload.get('dps').get('1')
    extracted_data_bat_2 = payload.get('dps').get('138')
    extracted_data_temp_1 = payload.get('dps').get('10')
    extracted_data_temp_2 = None
    extracted_data_battery_1_solar_input = payload.get('dps').get('103')
    extracted_data_battery_2_solar_input = None
    extracted_data_battery_1_output = payload.get('dps').get('108')
    extracted_data_battery_2_output = payload.get('dps').get('105')
    ac_is_on = payload.get('dps').get('109')  
    dc_is_on = payload.get('dps').get('112')  
    v12_is_on = payload.get('dps').get('111')  

    #DBS3000B data
    base64_strings = payload.get('dps').get('156')
    if(base64_strings != None) and len(base64_strings) > 24:
        print(base64_strings)
        decoded_data = base64.b64decode(base64_strings)
        parsed_values = parse_data(decoded_data)
        for type_id, value in parsed_values:
        
            if(type_id == 205):
                print(f'Type {type_id}: {value}')
                extracted_data_battery_2_solar_input = value
                battery_2_input = extracted_data_battery_2_solar_input
                status_json["battery_2_input"] = battery_2_input

            elif(type_id == 222):
                print(f'Type {type_id}: {value}')
                extracted_data_temp_2 = value
                battery_2_temp = extracted_data_temp_2
                status_json["battery_2_temp"] = battery_2_temp

    if((extracted_data_time == None) == False):    
        timestamp = extracted_data_time
        status_json["timestamp"] = timestamp
        
    if((extracted_data_bat_1 == None) == False):    
        battery_1_load = extracted_data_bat_1
        status_json["battery_1_load"] = battery_1_load

    if((extracted_data_bat_2 == None) == False):    
        battery_2_load = extracted_data_bat_2
        status_json["battery_2_load"] = battery_2_load

    if((extracted_data_temp_1 == None) == False):    
        battery_1_temp = extracted_data_temp_1
        status_json["battery_1_temp"] = battery_1_temp

    if((extracted_data_battery_1_solar_input == None) == False):    
        battery_1_solar_input = extracted_data_battery_1_solar_input
        status_json["battery_1_solar_input"] = battery_1_solar_input

    if((extracted_data_battery_1_output == None) == False):    
        battery_1_output = extracted_data_battery_1_output
        status_json["battery_1_output"] = battery_1_output

    if((extracted_data_battery_2_output == None) == False):    
        battery_2_output = extracted_data_battery_2_output
        status_json["battery_2_output"] = battery_2_output

    if((ac_is_on == None) == False):    
        ac_on = ac_is_on
        status_json["ac_on"] = ac_on

    if((v12_is_on == None) == False):    
        v12_on = v12_is_on
        status_json["v12_on"] = v12_on

    if((dc_is_on == None) == False):    
        dc_on = dc_is_on
        status_json["dc_on"] = dc_on


def send_payload(d, command):
    payload=d.generate_payload(tinytuya.CONTROL, command)
    d._send_receive(payload)


def run(server_class=http.server.HTTPServer, handler_class=DbsHTTPRequestHandler):
    server_address = (credentials.HTTP_SERVER_IP, credentials.HTTP_SERVER_PORT)
    httpd = server_class(server_address, handler_class)

    main_loop_thread = threading.Thread(target=main, daemon=True)
    main_loop_thread.start()
    
    logging.info("Starting httpd on port "+str(credentials.HTTP_SERVER_PORT)+"...")
    httpd.serve_forever()

def connect():
    logging.info("connect to 192.168.4.3")
    d = tinytuya.OutletDevice(credentials.dbs_id, '192.168.4.3', credentials.dbs_key)
    d.set_version(3.4)
    d.set_socketPersistent(True)

    payload = d.generate_payload(tinytuya.DP_QUERY)
    d.send(payload)

    time.sleep(1)

    data = d.receive()
    logging.info(data)

    return d


def main():
    global sendAcCmd
    global ac_on
    global timestamp

    d = connect()

    while(True):
        try:
            print(" > Send Heartbeat Ping < " + str(datetime.now()))
            logging.info(" > Send Heartbeat Ping < " + str(datetime.now()))

            payload = d.generate_payload(tinytuya.HEART_BEAT)
            d.send(payload)

            data = d.receive()
            process_payload(data)
            print(data)
            logging.info(str(data))

            data = d.status()
            process_payload(data)
            print(data)
            logging.info(str(data))

            if(ac_on == True and (battery_1_load < 10 or battery_2_load < 10)):
                logging.info("Auto turn AC off!")
                logging.info(str(battery_1_load))
                logging.info(str(battery_2_load))

                send_payload(d, {'109': False})
            
            if(sendAcCmd == True):
                sendAcCmd = False

                if(ac_on == False):
                    send_payload(d, {'109': True})
                else:
                    send_payload(d, {'109': False})  


            time.sleep(2)

        except Exception as e:
            logging.warning(str("Connection lost? reconnect!"))
            logging.warning(str(repr(e)))
            logging.warning(str(traceback.format_exc()))

            time.sleep(10)

            d = connect()



if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logging.warning(str(repr(e)))
        logging.warning(str(traceback.format_exc()))