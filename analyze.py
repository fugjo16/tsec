# -*- coding: utf-8 -*-

import os
import re
import sys
import csv
import time
import string
import logging

from datetime import datetime, timedelta
from os import mkdir
from os.path import isdir

class StockData():
	Date = datetime(2000,01,01)		# ?漱??Date
	Volume = 0.0					# ?漱??Trading Volume
	TurnoverValue = 0.0				# ?漱?? TurnOver in value
	Number = 0.0					# ?漱蝑 Number of Transaction
	OpenPrice = 0.0					# ???Open Price
	HighPrice = 0.0					# ?擃 Day High
	LowPrice = 0.0					# ?雿 Day Low
	ClosePrice = 0.0				# ?嗥??Close Price
	LastPrice = 0.0					# ?冽?嗥??Last Price
	Change = 0.0					# 瞍脰??孵榆 Change
	ChangePercent = 0.0				# 瞍脰? %
	ForeignInvestor = 0.0			# 憭?鞎瑁都頞?Foreign Investors Net Buy
	InvestTrust = 0.0				# ?縑鞎瑁都頞?Investment Trust Net Buy
	Dealer = 0.0					# ?芰??眺鞈?? Dealer Net Buy

	def __init__(self, data=[]):
		if len(data) < 10:
			return
		try:
			#Date = datetime(data[0])
			Volume = float(data[1])
			TurnoverValue = float(data[2])
			OpenPrice = float(data[3])
			HighPrice = float(data[4])
			LowPrice = float(data[5])
			ClosePrice = float(data[6])
			Change = float(data[7])
			LastPrice = ClosePrice - Change
			ChangePercent = Change / LastPrice
			ForeignInvestor = float(data[8])
			InvestTrust = float(data[9])
			Dealer = float(data[10])
		except:
			print data
		

class Analyzer():
	def __init__(self, prefix="data"):
		if not isdir(prefix):
			mkdir(prefix)
		self.prefix = prefix

	def _get_rows(self, stock_id):
		rows = []
		f = open('{}/{}.csv'.format(self.prefix, stock_id), 'rb')
		cr = csv.reader(f, delimiter=',', quotechar='|')
		for row in cr:
			rows.append(row)
			#print row
		f.close()
		return rows

	def _check_stock(self):
		rows = self._get_rows('0050')
		for row in rows:
			data = StockData(row)
			#print '{}'.format(data.ClosePrice)
		#for file in os.listdir(self.prefix):
		#	print file
