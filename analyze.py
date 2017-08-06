# -*- coding: utf-8 -*-

import os
import re
import sys
import csv
import time
import string
import logging
import ctypes  # An included library with Python install.


from datetime import datetime, timedelta
from os import mkdir
from os.path import isdir

def MessageBox(title, text, style=0x00):
	ctypes.windll.user32.MessageBoxW(0, text.decode('utf-8'), title.decode('utf-8'), style)

class StockData():
	def __init__(self, stock_id, data=[]):
		if len(data) <= 12:
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
			self.Val_K = float(data[12])												# K_9值
			self.Val_D = float(data[13])												# D_9值
			# Analyze Data
			self.MonthMaxTrust = 0		# 月投信最大買超量 (max top2平均)
			self.WeekMaxTrust = 0		# 周投信最大買超量
			self.WeekTotalForeign = 0	# 周外資平均外資買超比例
			self.MA5 = 0				# MA5
			self.MA20 = 0				# MA20


		except Exception, e:
			print 'ERROR: [{}]: {}'.format(stock_id, str(e))

	def __str__(self):  
		return '{},{},{}, {},{},{}, {},{},{},{},{}, {},{},{}'.format(self.id, '%d/%02d/%02d' % (self.Date.year-1911, self.Date.month, self.Date.day), '%.2f' % self.ChangePercent, 
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
		self.stocklist = []

	def _get_rows(self, stock_id):
		rows = []
		f = open('{}/{}.csv'.format(self.prefix, stock_id), 'rb')
		cr = csv.reader(f, delimiter=',', quotechar='|')
		for row in cr:
			rows.append(row)
			#print row
		del rows[0]
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
			
	def _analyze(self):
		for stock_id in self.stocklist:
			event_triger = False
			str_msg = ''

			try:
				# =========================== 買進訊號 ===========================
				max_ratio = (self.stock[stock_id][0].InvestTrust / self.stock[stock_id][0].MonthMaxTrust) if (self.stock[stock_id][0].MonthMaxTrust > 0) else 999
				if (self.stock[stock_id][0].InvestTrust > 0) and (max_ratio > 4):
					str_msg += '投信買超' + ('%.0f'%(self.stock[stock_id][0].InvestTrust/1000)) + '張 > 月最多' + ('%.0f'%(self.stock[stock_id][0].MonthMaxTrust/1000)) +'張  ['+ ('%.1f'%max_ratio) + '倍]\n'
					event_triger = True

				trust_ratio = (self.stock[stock_id][0].InvestTrust / self.stock[stock_id][0].Volume * 100)
				if trust_ratio > 5:
					str_msg += '昨日投信買超(' + '%.1f'%(trust_ratio) + '%) 大於5%\n'
					event_triger = True

				foreign_ratio = self.stock[stock_id][0].ForeignInvestor / self.stock[stock_id][0].Volume * 100
				if foreign_ratio > 50:
					str_msg += '昨日外資買超(' + '%.1f'%foreign_ratio + '%) 大於50%\n'
					event_triger = True

				if (self.stock[stock_id][0].Val_K > self.stock[stock_id][0].Val_D) and (self.stock[stock_id][1].Val_K < self.stock[stock_id][1].Val_D) and \
					 (self.stock[stock_id][1].Val_D < 30) and (self.stock[stock_id][1].Val_K < 30):
					str_msg += 'KD9黃金交叉 (' + '%.1f'%(self.stock[stock_id][0].Val_K) + '/' + '%.1f'%(self.stock[stock_id][0].Val_D) + ')\n'
					event_triger = True

				if (self.stock[stock_id][0].ClosePrice > self.stock[stock_id][0].MA20) and (self.stock[stock_id][1].ClosePrice < self.stock[stock_id][0].MA20):
					str_msg += '向上突破MA20 (' + '%.1f'%self.stock[stock_id][0].ClosePrice + ' > ' + '%.1f'%self.stock[stock_id][0].MA20 + ')\n'
					event_triger = True

				# =========================== 賣出訊號 ===========================
				if (self.stock[stock_id][0].Val_K < self.stock[stock_id][0].Val_D) and (self.stock[stock_id][1].Val_K > self.stock[stock_id][1].Val_D) and \
					 (self.stock[stock_id][1].Val_D > 70) and (self.stock[stock_id][1].Val_K > 70):
					str_msg += '!!! KD9死亡交叉 (' + '%.1f'%(self.stock[stock_id][0].Val_K) + '/' + '%.1f'%(self.stock[stock_id][0].Val_D) + ')\n'
					event_triger = True

				if (self.stock[stock_id][0].ClosePrice < self.stock[stock_id][0].MA20) and (self.stock[stock_id][1].ClosePrice > self.stock[stock_id][0].MA20):
					str_msg += '!!! 向下突破MA5 (' + '%.1f'%self.stock[stock_id][0].ClosePrice + ' < ' + '%.1f'%self.stock[stock_id][0].MA20 + ')\n'
					event_triger = True	
			except:
				print "Analyze Error: ", sys.exc_info()[0]
			# =========================== Send Out Message ===========================
			if event_triger == True:
				#MessageBox(stock_id, str_msg)
				print stock_id + ':\n' + str_msg.decode('utf-8')
		
	def _get_analyze_data(self):
		for stock_id in self.stocklist:
			# Initialize data
			self.stock[stock_id][0].MA5 = self.stock[stock_id][0].MA20 = self.stock[stock_id][0].WeekTotalForeign = 0
			# for week data
			for i in range(5):
				if self.stock[stock_id][i].InvestTrust > self.stock[stock_id][0].WeekMaxTrust:
					self.stock[stock_id][0].WeekMaxTrust = self.stock[stock_id][i].InvestTrust
				if self.stock[stock_id][i].Volume != 0:
					self.stock[stock_id][0].WeekTotalForeign += (self.stock[stock_id][i].ForeignInvestor / self.stock[stock_id][i].Volume) * 100 / 5
				self.stock[stock_id][0].MA5 += self.stock[stock_id][i].ClosePrice / 5
			#	if stock_id == '2317':
			#		print str(stock_id) + ': ' + str(self.stock[stock_id][0].WeekTotalForeign)

			# for month data
			month_trust_max1 = month_trust_max2 = 0
			for i in range(1, 20):
				if self.stock[stock_id][i].InvestTrust > month_trust_max1:
					month_trust_max2 = month_trust_max1
					month_trust_max1 = self.stock[stock_id][i].InvestTrust
				elif self.stock[stock_id][i].InvestTrust > month_trust_max2:
					month_trust_max2 = self.stock[stock_id][i].InvestTrust
				self.stock[stock_id][0].MA20 += self.stock[stock_id][i].ClosePrice / 20
			self.stock[stock_id][0].MonthMaxTrust = (month_trust_max1 + month_trust_max2) / 2

			#print str(self.stock[stock_id][0].ClosePrice) + ': '+ str(self.stock[stock_id][0].MA5) + ", " + str(self.stock[stock_id][0].MA20) 

	def _get_stock_info(self): 
		self._get_list()
		for stock_id in self.stocklist:
			rows = self._get_rows(stock_id)
			stock_days = []
			
			for row in rows:
				data = StockData(stock_id, row)
				stock_days.append(data)
				
			self.stock[stock_id] = stock_days
		#print self.stock['2317'][0]

	def _get_list(self):
		file = open('stocklist.csv', 'rb')
		for line in file:
			for stock_file in os.listdir(self.prefix):
				if line.strip('\r\n') == stock_file.strip('.csv'):
					self.stocklist.append(line.strip('\r\n'))		
		file.close()



def main():
	analyzer = Analyzer()
 	analyzer._get_stock_info()
 	analyzer._get_analyze_data()
 	analyzer._analyze()

def setup():
	pass

if __name__ == '__main__':
	setup()
	main()    
