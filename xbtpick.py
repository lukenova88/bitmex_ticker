#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 19:48:23 2020

@author: Luke Nova
"""

import time
from datetime import datetime
import requests, json
import socket
import urllib2
import numpy as np
import time
from datetime import date
from datetime import datetime
from pytz import timezone


now = datetime.now()
TCP_PORT = 61123
TCP_IP = '127.0.0.1'
BUFFER_SIZE = 512  # Normally 1024, but we want fast response

pricechange = '0'    
xbt_price_now = 0
xbt_price_bef = 0
displayvalue = '0'
maxlight = 100

while True:
    
    response = requests.get("https://www.bitmex.com/api/v1/trade?symbol=XBT&count=1&reverse=true").json()
    time.sleep(3)
    getprices = requests.get("https://www.bitmex.com/api/v1/trade/bucketed?binSize=1h&partial=true&symbol=XBT&count=25&reverse=true").json()
	
    if "error" in getprices:
        time.sleep(5)
        print(getprices)
        continue    

    if "error" in response:
        time.sleep(5)
        print(response)
        continue

    prices = [0,0,0,0,0,0,0,0]
    rngnums = [0,0,0,0,0,0,0,0]
    outchart = [0,0,0,0,0,0,0,0]
    
    h = 7
    while h >= 0:   #get prices for last 8 hours
       	prices[h] = int(getprices[h]['close'])
       	#print(str(prices[h]) + ' ' + str(h))
       	h -= 1

    #print(max(prices))
    #print(min(prices))
    step = float(max(prices) - min(prices)) / 7
    #print range
    #print step
    
    i = 0    
    while i < 8:    #get range prices
        rngnums[i] = int(min(prices) + (i * step))
        #print rngnums[i]
        i += 1
    
        #print '-------'    
    
    def closest(rngnums, K): #this function will find closest value from range
      
        rngnums = np.asarray(rngnums) 
        idx = (np.abs(rngnums - K)).argmin() 
        return rngnums[idx] 
      
    j = 7
    m = 0
    while j >= 0:    #get values for led matrix chart
        K = prices[j]
        #print('value ' + str(prices[j]) + ' is closest to ' + str(closest(rngnums, K)) + ' from range ' + str(rngnums)) 
        l = 7
        while l >= 0:
            if closest(rngnums, K) == rngnums[l]:
                #print l
                outchart[m] = l
            l -= 1
        j -= 1
        m += 1
    
#    print(outchart)

    if int(xbt_price_now) != int(response[0]['price']): 	    
	xbt_price_now = int(response[0]['price'])
        
        if xbt_price_now > xbt_price_bef:
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		printline = current_time + ' ▲ ' + str(xbt_price_now)
		#print printline
		pricechange = 'U'
		pricevar = pricechange + ';' + str(xbt_price_now) + ';' + str(outchart)
		#print pricevar
    
       	if xbt_price_now < xbt_price_bef:
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		printline = current_time + ' ▼ ' + str(xbt_price_now)
		#print printline
		pricechange = 'D'
		pricevar = pricechange + ';' + str(xbt_price_now) + ';' + str(outchart)
		#print pricevar

	xbt_price_bef = xbt_price_now
	displayvalue = '0'	

	ts = time.time()
	utc_offset = (datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()
	utc_offset = int(utc_offset / 3600)
#	print utc_offset


	daylight = requests.get("https://api.met.no/weatherapi/sunrise/2.0/.json?lat=50.026166&lon=14.528966&date=2020-04-18&offset=+0" + str(utc_offset) + ":00").json()
	sunrise = daylight["location"]["time"][0]["sunrise"]["time"][11:-9]
	sunset  = daylight["location"]["time"][0]["sunset"]["time"][11:-9]
#	print sunrise
#	print sunset
 		
    
	#get timestamps
	sunrise_hours, sunrise_minutes = sunrise.split(":")
	sunset_hours, sunset_minutes   = sunset.split(":")
	sunrise_minute_count = int(sunrise_hours)*60 + int(sunrise_minutes)
	sunset_minute_count = int(sunset_hours)*60 + int(sunset_minutes)
#	print sunrise_minute_count
#	print sunset_minute_count
	timenow = datetime.now().strftime('%H:%M')
	timenow_hours, timenow_minutes = timenow.split(":")
	timenow_hours = str(timenow_hours)
	timenow_minutes = str(timenow_minutes)
#	print 'hours ' + str(timenow_hours)
#	print 'mins  ' + str(timenow_minutes)
	timenow_minute_count = int(timenow_hours)*60 + int(timenow_minutes)
	half_day = sunset_minute_count - sunrise_minute_count
#	timenow_minute_count = 1000
#	print 'timenow_minute_count ' + str(timenow_minute_count)

	#set display brightness according to light outside
	if (timenow_minute_count > sunrise_minute_count and timenow_minute_count < sunset_minute_count):
        	if timenow_minute_count < half_day:
			x = float(timenow_minute_count - sunrise_minute_count) / float(half_day / 2)
        		displayvalue = int(x * maxlight)
       		if timenow_minute_count >= half_day:
			x = float(sunset_minute_count - timenow_minute_count) / float(half_day / 2)
          		displayvalue = int(x * maxlight)
#	print displayvalue
			
		
	pricevar = pricevar + ';' + str(displayvalue)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	s.send(str(pricevar))
	data = s.recv(BUFFER_SIZE)
#	print pricevar
#	print data	
	
	time.sleep(3)
