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
	def __init__(self, data=[]):
		if len(data) < 10:
			return
		self.Date = datetime.strptime(re.sub("/", "", data[0].strip()), "%Y%m%d")
		self.Volume = float(data[1])
		self.TurnoverValue = float(data[2])
		self.OpenPrice = float(data[3])
		self.HighPrice = float(data[4])
		self.LowPrice = float(data[5])
		self.ClosePrice = float(data[6])
		self.Change = float(data[7])
		self.LastPrice = self.ClosePrice - self.Change
		self.ChangePercent = self.Change / self.LastPrice
		self.ForeignInvestor = float(data[8])
		self.InvestTrust = float(data[9])
		self.Dealer = float(data[10])
		

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
			print '{}'.format(data.Date)
		#for file in os.listdir(self.prefix):
		#	print file
