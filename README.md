# Dabbsson_control

This repository is about getting access to your Dabbsson DBS2300 and Dabbsson DBS3000B powerstation via WiFi without using the official app. This is not a ready-made solution but only an approach. 

## Why?

From my point of view, the DBS2300 and DBS3000B are good products and I am very happy. The only disadvantage is that only the official app can be used for communication.

Using the powerstation just with the Dabbsson app (pressing stupid buttons) is not what I needed. I wanted to automate switching the power outputs according to the current inputs and battery state of charge.

In addition to that I don´t want my devices "calling home". That was something I observed while I did my first investigations using Wireshark. Unfortunately all traffic was encrypted.


## Setup

Therefore after getting control (see "What to do?") I am using a Raspberry Pi Zero W to control the powerstation. The Rpi creates an WiFi Access Point to which the DBS2300 connects. The Rpi does not provide internet access over the wifi interface. The Rpi is connected over a usb-to-ethernet-adapter to my home network and provides a HTTP-server to access the data or to control the device.

## What to do?

After a while I figured out that the DBS2300 is using [Tuya](https://en.tuya.com/). 
To do the first steps you can follow the instructions of [TinyTuya](https://github.com/jasonacox/tinytuya/tree/master). Basically getting an developer [Account] (https://developer.tuya.com/en/) and connect your DBS2300 with the official Tuya Smart app to generate a local key and get the device id. Without a local key, you can no communicate with your device. 


Be aware the official Dabbsson app will not work anymore after that! I haven´t tried to go back to the official app. All you do is at your own risk!

You can use [TinyTuya](https://github.com/jasonacox/tinytuya/tree/master) to control your device as shown in this repository.


Example data from the DBS2300 looks like this:
```json
{'protocol': 4, 't': 63848, 'data': {'dps': {'156': 'zQAAAADOAAAAANAAAAAA0QAAAADcExwhAN0AAAAB3gAAABs='}}}

{'protocol': 4, 't': 63848, 'data': {'dps': {'1': 9, '2': 4761, '10': 19, '103': 0, '104': 0, '105': 0, '106': 0, '110': 0, '108': 0, '138': 25, '139': 0}}, 'dps': {'1': 9, '2': 4761, '10': 19, '103': 0, '104': 0, '105': 0, '106': 0, '110': 0, '108': 0, '138': 25, '139': 0}}

```
Example key-value pairs

| key | value |
|-----|-------|
| 1   |   State of charge DBS2300 in %   |
| 10  |   Temperature of DBS2300     |
| 103 |   DC-Input of DBS2300    |
| 105 |   DC-Output of DBS3000B    |
| 108 |   Output of DBS2300    |
| 109 |   AC-Out on/off    |
| 111 |   5V-Out on/off     |
| 112 |   12V-Out on/off     |
| 138 |   State of charge DBS3000B in %     |
| 156 |   Base64 encoded information of DBS3000B (including keys 205, 206, 208, 209, 220, 221, 222) |


The HTTP-Server (see checkDBS2300.py) will give you on http://localhost:9980/status some of the information:

```json
{"timestamp": 64138, "battery_1_load": 9, "battery_2_load": 25, "battery_1_temp": 18, "battery_2_temp": 27, "battery_1_solar_input": 0, "battery_2_input": 0, "battery_1_output": 0, "battery_2_output": 0, "ac_on": false, "dc_on": false, "v12_on": false}
```

With http://localhost:9980/set you can toggle the AC-Output. In addition the AC-Output is turned off if the state of charge gets below 10%.


## References
* Tuya - : https://developer.tuya.com/
* Dabbsson - : https://www.dabbsson.com/
* TinyTuya - : https://github.com/jasonacox/tinytuya/


## Legal Disclaimer
As mentioned before: 

This is not a ready-made solution but only an approach!
All you do is at your own risk!

The information and tools provided in this repository are intended for educational and research purposes only. The author is not responsible for any misuse or damage resulting from the use or misuse of the information or software provided here.

This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. Use this software at your own risk.