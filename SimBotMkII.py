#!/usr/bin/python

#Bot MK II

#See SimBot Mk I for more info.

#Mk II seeks to add fees into account and analysis of the order book to ensure transaction go through.




import requests	
import time
import hmac
import hashlib
import json

Wallet = [1, 0]	#bitcoin and USD values

#initial values to not satisfy if statements
SellTime = False
BuyTime = False
SellTS = 30000000000
ReferencePrice = int(input('BTC Price one hour ago: '))
starttime = time.time()
print(int(time.time()))
PredictedPrice = 0
SellPrice = 0
Trade = 'Sell'


while True:	#Loop that executes every x seconds, see last line
	Tick = (int(time.time()))
	ticker = requests.get("https://cex.io/api/last_price/BTC/USD")	# prints the last traded price
	LastPrice = json.loads(ticker.text)
#Interpolate last hour of data and extrapolate to predict highs and lows.
#Recalcualtes after avery two minutes, or each time a tsell order is made. 
	if (Tick % 200 == 0 or int(starttime) == Tick or Trade == 'Buy'):
		print('---------------')
		OneHourPrice = ReferencePrice
		ReferenceTime = time.time()	#Used to calculate predicted price
		ReferencePrice = int(float(LastPrice['lprice']))
		Delta = (ReferencePrice - OneHourPrice) / 36000 	#average change persecond of past hour
		PredictedPrice = ReferencePrice + (Delta * (time.time() - ReferenceTime))
	if (PredictedPrice) != 0:
		PredictedPrice = ReferencePrice + (Delta * (time.time() - ReferenceTime))
	print(LastPrice['lprice'], PredictedPrice)


#Place Sell Order

	if (float(PredictedPrice) <= float(LastPrice['lprice']) - 30 and Trade == 'Sell'):
		SellTotal = requests.post('https://cex.io/api/convert/BTC/USD', data = {'amnt': .01})
		SellPrice = float(LastPrice['lprice'] - float(LastPrice['lprice'] * .0002))
		SellTS = time.time()
		sell_data = json.loads(SellTotal.text)
		print('Sell')
		Wallet[1] += float(sell_data['amnt'])
		Wallet[0] -= .01
		print(Wallet)
		Trade = 'Buy'

#Place Buy Order 																				or concede loss
	if (((float(SellPrice) >= float(LastPrice['lprice']) + 30) or (time.time() - SellTS > 120)) and Trade == 'Buy' ):
		BuyTotal = requests.post('https://cex.io/api/convert/BTC/USD', data = {'amnt': 1})
		sell_data = json.loads(BuyTotal.text)
		print('Buy')
		BTC = Wallet[1] / sell_data['amnt']
		Wallet[0] += BTC
		Wallet[1] = 0
		print(Wallet)
		Trade = 'Sell'




	time.sleep(2 - (time.time() - starttime) % 2) # sleeps for given time. ints must == && >1