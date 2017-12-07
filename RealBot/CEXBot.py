#!/usr/bin/python3

#Bot MK II

# This version includes general streamlined features, better implementation of price changes, 
#Along with other readablilty fixes. 
#Will change instant order to market order to get more competitive prices & avoid taker fees.
#Also may choose to change how to trigger sell order. Buy Order trigger should be okay.

#Try to minimize time fiat currency is stored to get those sick crypto gains
#Sell high, buy low, not the other way around.
#any variable needing to be int or float should be converted at declaration.

#CARE WHEN BUILDING, AS WILL SELL BTC 


import time
import hmac
import hashlib
import json
import requests	

def Sig():	#Used to set up Private API calls.
	userID = 'up111447887'
	api_key = '5buowopJaCaHWQKdECauvjHfMs'
	API_SECRET = str.encode('FawVVo9lIwVZvKdMTRghFauVQj4')
	nonce = str(int(time.time()))
	message = str.encode(nonce + userID + api_key)
	signature = hmac.new(API_SECRET, msg=message, digestmod=hashlib.sha256).hexdigest().upper()

	return ([api_key, signature, nonce])

#Initial Conditions
Trade = 'Sell'
TS = 30000000000	#to avoid triggering buy order before first sell.
StartTime = time.time()
#Get Reference Price	

while True:	#loops forever, every time as defined by the last line of the program.
	CurrentPrice = float(json.loads(requests.get("https://cex.io/api/last_price/BTC/USD").text)['lprice'])
	print(CurrentPrice)


	#Eventually, the analysis will yield:
	TargetPrice = 0
	#Once this is achieved, buy and sell orders can be run.

#Check to see if orders were completed to seitch to other trading scheme.
	APICall = Sig()
	Parameters = {'key' : APICall[0], 'signature' : APICall[1], 'nonce' : APICall[2]}
	OpenOrders = json.loads(requests.post('https://cex.io/api/open_orders/', data = Parameters).text)
	print(OpenOrders)
	if (OpenOrders == [] and Trade == 'Selling'): #Trade complete
		Trade = 'Buy'
		TS = 30000000000
	if(OpenOrders ==[] and Trade == 'Buying'):
		Trade = 'Sell'
		TS = 30000000000

#Cancel Order
#Takes priority as it is the catalyst for the trade cycle.
#Will only be able to cancel current active order.
	if time.time() - TS > 10 :	#cancels after 10 seconds
		APICall = Sig()
		Parameters = {'key' : APICall[0], 'signature' : APICall[1], 'nonce' : APICall[2], 'id' : ID}
		Cancel = requests.post('https://cex.io/api/cancel_order/', data = Parameters)
		if Trade == 'Selling':	#reverts attempt same order again.
			Trade = 'Sell'
		if Trade == 'Buying':
			Trade = 'Buy'
		TS = 30000000000

#Place Sell Order
#Trigger for a profit cycle	
#How to calculate reasonable sell order?

	if (Trade == 'Sell' and TargetPrice <= CurrentPrice - 30): #Will sell current price is $30 over expected, should break even
		APICall = Sig()
		Parameters = {'key' : APICall[0], 'signature' : APICall[1], 'nonce' : APICall[2], 'type' : 'sell', 'amount' : .01, 'price': CurrentPrice + 100}
		SellOrder = json.loads(requests.post('https://cex.io/api/place_order/BTC/USD', data = Parameters).text)
		#print(SellOrder)
		ID = SellOrder['id']
		TS = float(SellOrder['time'])
		SellPrice = float(SellOrder['price'])
		Trade = 'Selling' #Switch to looking for buy


		APICall = Sig()
		Parameters = {'key' : APICall[0], 'signature' : APICall[1], 'nonce' : APICall[2]}
		Account = json.loads(requests.post('https://cex.io/api/balance/', data = Parameters).text)
		print(Account['BTC']['available'], Account['USD']['available'])


#Place Buy Order 
#Only triggered when a sell order is made or when the previous buy order is cancelled

	if (Trade == 'Buy' and SellPrice > CurrentPrice + 30):
		APICall = Sig()
		Parameters = {'key' : APICall[0], 'signature' : APICall[1], 'nonce' : APICall[2]}
		Account = json.loads(requests.post('https://cex.io/api/balance/', data = Parameters).text)
		Fiat = float(Account['USD']['available'])
		BTC = Fiat / float(json.loads(requests.post('https://cex.io/api/convert/BTC/USD', data = {'amnt' : 1}).text)['amnt'])
		Parameters = {'key' : APICall[0], 'signature' : APICall[1], 'nonce' : APICall[2], 'type' : 'buy', 'amount': BTC , 'price': CurrentPrice - 1}
		BuyOrder = json.loads(requests.post('https://cex.io/api/place_order/BTC/USD', data = Parameters).text)
		#print(BuyOrder)
		TS = float(BuyOrder['time'])
		ID = BuyOrder['id']
		Trade = 'Buying'

		APICall = Sig()
		Parameters = {'key' : APICall[0], 'signature' : APICall[1], 'nonce' : APICall[2]}
		Account = json.loads(requests.post('https://cex.io/api/balance/', data = Parameters).text)
		print(Account['BTC']['available'], Account['USD']['available'])





	#How long program goes between iterations
	time.sleep(2 - (time.time() - StartTime) % 2) # sleeps for given time. ints must == && >1
