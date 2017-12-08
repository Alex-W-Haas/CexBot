#!/usr/bin/python3

#SimBot MK III

#Strategy: RSI Analysis to determine swings

#RSI (Relative Strength Index) is an indication of the markets momentum oscillations.
# Value between 0 and 100, meadian 50. If the index is high (>70), the asset has been rising
#and will likely correct negatively, and a low index means the opposite.
#Typically calculated over a 14-day period. may just do seven. who knows.
#Trigger will be high RSIs.

# This version includes general streamlined features, better implementation of price changes, 
#Along with other readablilty fixes. 
#Will change instant order to market order to get more competitive prices & avoid taker fees.
#Also may choose to change how to trigger sell order. Buy Order trigger should be okay.

#Try to minimize time fiat currency is stored to get those sick crypto gains
#Sell high, buy low, not the other way around.
#any variable needing to be int or float should be converted at declaration.

#New Parameter 'Hodl' for when current RSI near 50, not pressure to sell. 
#Also add parameter to look for sell walls @ 100 marks

import time
import string
import hmac
import hashlib
import json
import requests	

#Initial Conditions
Trade = 'Hodl'
TS = 30000000000	#to avoid triggering buy order before first sell.
StartTime = int(time.time())
Date = time.strftime('%Y%m%d')
print(Date)

#Use OHLCV (Open High Low Close Volume) chart which pulls the last month of data 
#OHLCV dat is stored in a list in a list in a dict. 
#But the content of the dict is just a string, not a nested list.
#Fuck, this is going to get messy.
OHLCV = json.loads(requests.get('https://cex.io/api/ohlcv/hd/20171207/BTC/USD').text)
OneDayOHLCV = OHLCV['data1d']
DayLists = []

#I am a fucking god for making this work. 
for i in OneDayOHLCV:	#For each damn character in the string
	
	if (i == 'u' or i == "'"):
		continue	#skip the extra shit we dont need.

	if i == ']':
		List = str(List)
		List = List.split(",")
		if len(List) > 1:
			DayLists.append(List)
		List = ''
	if i =='[':	#Check to find start of lists.
		List = ''	#Clear the strings from the Nested Lists
		continue
	List += i
#Daylists are all strings, need to be converted to ints and floats when used.
#Daylists is, for each nested list: [Time, Open, High, Low, Close, Volume]

#Initially Calculate RSI
U = 0
n = 0
D = 0
m = 0
for k in (DayLists):
	if float(k[4]) > float(k[1]):
		U += float(k[4]) - float(k[1])
		n += 1	
	if float(k[1]) > float(k[4]):
		D += float(k[1]) - float(k[4])
		m += 1	
RS = (U/n)/(D/m)
RSI = 100 - (100/(1+RS))
#And after every minute(?), the newest data will be added to eithr U or D and will recalcualte
#Eventually, the analysis will yield:

HighPrice = float(json.loads(requests.get('https://cex.io/api/ticker/BTC/USD').text)['bid'])
LowPrice = float(json.loads(requests.get('https://cex.io/api/ticker/BTC/USD').text)['ask'])
NowPrice = (HighPrice + LowPrice) / 2	#Will actually become Previous Price when called
while True:	#loops forever, every time as defined by the last line of the program.
	Tick  = int(time.time())
	PreviousPrice = NowPrice
	NowPrice = float(json.loads(requests.get("https://cex.io/api/last_price/BTC/USD").text)['lprice'])
	print(NowPrice)
#Recalculate RSI
	if NowPrice > PreviousPrice:
		U += NowPrice - PreviousPrice
		n += 1
	if NowPrice < PreviousPrice:
		D += PreviousPrice - NowPrice
		m += 1
	RS = (U/n)/(D/m)
	RSI = 100 - (100/(1+RS))
	print(RSI)
		

#Place Sell Order

	if (RSI > 75 and Trade == 'Sell'):
		SellTotal = requests.post('https://cex.io/api/convert/BTC/USD', data = {'amnt': .01})
		SellPrice = (float(LastPrice['lprice']))
		#print(SellPrice)
		SellTS = time.time()
		sell_data = json.loads(SellTotal.text)
		print('Sell')
		Wallet[1] += float(sell_data['amnt']) * .998
		Wallet[0] -= .01
		print(Wallet)
		Trade = 'Buy'

#Place Buy Order 											or concede loss
	if ((RSI > 30 or (time.time() - SellTS > 200)) and Trade == 'Buy' ):
		BuyTotal = requests.post('https://cex.io/api/convert/BTC/USD', data = {'amnt': 1})
		sell_data = json.loads(BuyTotal.text)
		print('Buy')
		BTC = Wallet[1] / sell_data['amnt'] *.998
		Wallet[0] += BTC
		Wallet[1] = 0
		print(Wallet)
		Trade = 'Sell'





	#How long program goes between iterations
	time.sleep(2 - (time.time() - StartTime) % 2) # sleeps for given time. ints must == && >1
