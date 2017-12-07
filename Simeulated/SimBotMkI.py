#!/usr/bin/python

#Bot MK I

#This program is designed, with conjunction with Cex.io's API, to 
#automatically trade Bitcoin at designated times. What are those times?
#we shall see.

#Currently looking to create a linear trend line over the past hour
#to determine any significant deviations in price
#What Mitch refers to as 'the ruler method'

#Cex.io can only handle 60 API calls a minute. We will keep a minimum
# of 2 seconds to avoid clogging the system.

#This program uses a simulated wallet to refine paremeters on when to buy/sell
#risk free!

#also assumes orders go thrugh immideiately

#Initial 1 hr test with orders  30 of trendline net with no fees, .001543 BTC.


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
	if (Tick % 200 == 0 or int(starttime) == Tick):
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
		SellPrice = float(LastPrice['lprice']) *.0098
		SellTS = time.time()
		sell_data = json.loads(SellTotal.text)
		print('Sell')
		Wallet[1] += float(sell_data['amnt'])
		Wallet[0] -= .01
		print(Wallet)
		Trade = 'Buy'

#Place Buy Order 																				or concede loss
	if (((float(SellPrice) > float(LastPrice['lprice'])) or (time.time() - SellTS > 120)) and Trade == 'Buy' ):
		BuyTotal = requests.post('https://cex.io/api/convert/BTC/USD', data = {'amnt': 1})
		sell_data = json.loads(BuyTotal.text)
		print('Buy')
		BTC = Wallet[1] / sell_data['amnt'] *.0098
		Wallet[0] += BTC
		Wallet[1] = 0
		print(Wallet)
		Trade = 'Sell'




	time.sleep(2 - (time.time() - starttime) % 2) # sleeps for given time. ints must == && >1
