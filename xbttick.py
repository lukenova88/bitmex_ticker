#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import re
import requests
import time
from datetime import datetime
from datetime import date
from pytz import timezone
import argparse
import socket

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, TINY_FONT, SINCLAIR_FONT, CP437_FONT, LCD_FONT
from PIL import ImageFont

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=32, height=8,  block_orientation=-90, contrast = 100)

now = datetime.now()
TCP_PORT = 61123
TCP_IP = '127.0.0.1'
BUFFER_SIZE = 512  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

fontnum  = ImageFont.truetype("/home/pi/BitMEX/luke-led-matrix.ttf", 8)

inverted = [0,0,0,0,0,0,0,0,0,0,0,0,0]

msg = "initializing XBT ticker by LUKE NOVA"
show_message(device, msg, fill="green", font=proportional(TINY_FONT), scroll_delay=0.035)

while True:
	now = datetime.now()
	current_time = now.strftime("%H%M%S")
#	print(current_time)
	if (current_time[2:-2] == '59' and current_time[4:-1] == '5'):
		msg = "XBT ticker by LUKE NOVA"
		show_message(device, msg, fill="green", font=proportional(TINY_FONT), scroll_delay=0.02)

	else:

		conn, addr = s.accept()
		data = conn.recv(BUFFER_SIZE)
	        if not data: break
#	        print "received data:", data
#		conn.send(data)  # echo
        	conn.close()

		print data
		datalist = data.split(";")
		outchart = data.split(";")[2]
 		displayvalue = int(data.split(";")[3])
		outchart = outchart[1:-1]
		outchart = outchart.split(',')
		device = max7219(serial, width=32, height=8,  block_orientation=-90, contrast=displayvalue)
		
		k = 0
		while k < 8:
			inverted[k] = abs(int(outchart[k]) - 7)
#			print outchart[k]
#			print inverted[k]
			k += 1
		
		with canvas(device) as draw:
			draw.point((0,inverted[0]), fill="green")
                        draw.point((1,inverted[1]), fill="green")
                        draw.point((2,inverted[2]), fill="green")
                        draw.point((3,inverted[3]), fill="green")
                        draw.point((4,inverted[4]), fill="green")
                        draw.point((5,inverted[5]), fill="green")
                        draw.point((6,inverted[6]), fill="green")
                        draw.point((7,inverted[7]), fill="green")
			draw.text((10, 0), datalist[1], fill="green", font=fontnum)

