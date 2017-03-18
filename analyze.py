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
	def __init__(self, stock_id, data=[]):
		if len(data) < 10:
			return
		try:
			self.id = stock_id
			_date = data[0].split("/")
			self.Date = datetime(int(_date[0])+1911, int(_date[1]), int(_date[2])) 		# 成交日期 Date
			self.Volume = float(data[1])												# 成交量 Volume
			self.TurnoverValue = float(data[2])											# 成交金額 Turn Over Value
			self.OpenPrice = float(data[3])												# 開盤價 Open Price
			self.HighPrice = float(data[4])												# 最高價 High Price
			self.LowPrice = float(data[5])												# 最低價 Low Price
			self.ClosePrice = float(data[6])											# 收盤價 Close Price
			self.Change = float(data[7])												# 漲跌價差 Change
			self.LastPrice = self.ClosePrice - self.Change								# 昨日收盤價 Last Price 
			self.ChangePercent = (self.Change / self.LastPrice * 100) if (self.LastPrice > 0) else 0				# 漲跌幅 % 
			self.NumberTransaction = float(data[8])										# 成交筆數 Number of Transactions
			self.ForeignInvestor = float(data[9])										# 外資買賣超 Foreign Investor Net Buy 
			self.InvestTrust = float(data[10])											# 投信買賣超 Invest Trust Net Buy 
			self.Dealer = float(data[11])												# 自營商買賣超 Dealer Net Buy
		except:
			print 'ERROR: [{}]: {}'.format(stock_id, str(data))

	def __str__(self):  
		return '{},{},{}, {},{},{}, {},{},{},{},{}, {},{},{}\n'.format(self.id, '%d/%02d/%02d' % (self.Date.year-1911, self.Date.month, self.Date.day), '%.2f' % self.ChangePercent, 
							self.Volume, self.TurnoverValue, self.NumberTransaction, 
							self.OpenPrice, self.HighPrice, self.LowPrice, self.ClosePrice, self.Change, 
							self.ForeignInvestor, self.InvestTrust, self.Dealer)
'''
		return '[{}] {}: {}% > {}, {}'.format(self.id, '%d/%02d/%02d' % (self.Date.year-1911, self.Date.month, self.Date.day), '%.2f' % (self.ChangePercent),
							[self.OpenPrice, self.HighPrice, self.LowPrice, self.ClosePrice, self.Change],
							[self.ForeignInvestor, self.InvestTrust, self.Dealer],
							)
'''
class Analyzer():
	def __init__(self, prefix="data"):
		if not isdir(prefix):
			mkdir(prefix)
		self.prefix = prefix
		self.stock = {}

	def _get_rows(self, stock_id):
		rows = []
		f = open('{}/{}.csv'.format(self.prefix, stock_id), 'rb')
		cr = csv.reader(f, delimiter=',', quotechar='|')
		for row in cr:
			rows.append(row)
			#print row
		f.close()
		return rows

	def _record(self, row):
		''' Save row to csv file '''
		f = open('analyze.csv', 'ab')
		f.write(row)
		f.close()
	def _record_stock(self, data):
		cnt = 0
		if data.ChangePercent > 3:
			cnt = 10
			self._record('\n')

			if cnt > 0:
				print str(data)
				self._record(str(data))
				cnt -= 1
				#print ', '.join("%s: %s" % item for item in vars(stock_days[index]).items())
			

	def _check_stock(self):
		f = open('analyze.csv', 'wb')
		f.close()
		#for file in os.listdir(self.prefix):
		stock_id = '2317'	#file.strip('.csv')
		rows = self._get_rows(stock_id)
		stock_days = []
		
		for row in rows:
			data = StockData(stock_id, row)
			stock_days.append(data)
			
		self.stock[stock_id] = stock_days

def main():
	analyzer = Analyzer()
 	analyzer._check_stock()

if __name__ == '__main__':
	main()    