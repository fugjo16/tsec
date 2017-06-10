# -*- coding: utf-8 -*-

import os
import re
import sys
import csv
import time
import string
import logging
import requests
import argparse
from lxml import html
from datetime import datetime, timedelta

from os import mkdir
from os.path import isdir

from analyze import Analyzer

class Crawler():
    def __init__(self, prefix="data"):
        ''' Make directory if not exist when initialize '''
        if not isdir(prefix):
            mkdir(prefix)
        self.prefix = prefix
        self.tse_data = {}
        self.fund_data = {}

    def _is_number(self, str):
        return str.replace('.','',1).replace('-','',1).isdigit()

    def _clean_row(self, row):
        ''' Clean comma and spaces '''
        for index, content in enumerate(row):
            row[index] = re.sub(",", "", content.strip())
            #row[index] = filter(lambda x: x in string.printable, row[index])
            if (index > 0) and (self._is_number(row[index])) == False:     
                row[index] = 0
        return row

    def _record(self, stock_id, row):
        ''' Save row to csv file '''
        f = open('{}/{}.csv'.format(self.prefix, stock_id), 'ab')
        cw = csv.writer(f, lineterminator='\n')
        cw.writerow(row)
        f.close()
    def _check_date(self, date_str):
        status = True
        try:
            f = open('{}/{}.csv'.format(self.prefix, '0050'), 'rb')
            cr = csv.reader(f, delimiter=',', quotechar='|')
            
            for row in cr:
                if date_str == row[0]:
                    status = False
            f.close()
        except:
            status = True
        return status

    def _get_fund_data(self, date_str):
        payload = {
            'download': '',
            'qdate': date_str,
            'select2': 'ALLBUT0999',
            'sorting': 'by_stkno'
        }
        url = 'http://www.twse.com.tw/ch/trading/fund/T86/T86.php'
        # Get html page and parse as tree
        page = requests.post(url, data=payload)
        if not page.ok:
            logging.error("Can not get Fund data at {}".format(date_str))
            return
        # Parse page
        tree = html.fromstring(page.text)

        self.fund_data.clear()
        for tr in tree.xpath('//table[2]/tbody/tr'):
            fund = tr.xpath('td/text()')
            row = self._clean_row([
                fund[4],    #外資買賣超
                fund[7],    #投信買賣超
                fund[8],    #自營商買賣超
            ])
            self.fund_data[fund[0].strip(' ')] = row

    def _get_tse_data(self, date_str):
        first_day = datetime(2017, 6, 9)
        date_tuple = (first_day.year, first_day.month, first_day.day)
        date_str = '{0}{1:02d}{2:02d}'.format(first_day.year, first_day.month, first_day.day)
        
        url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX'

        query_params = {
            'date': date_str,
            'response': 'json',
            'type': 'ALLBUT0999',
            '_': str(round(time.time() * 1000) - 500)
        }
        #url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX'

        # Get json data
        page = requests.get(url, params=query_params)

        if not page.ok:
            logging.error("Can not get TSE data at {}".format(date_str))
            return

        content = page.json()
        self.tse_data.clear()

        # For compatible with original data
        date_str_record = '{0}/{1:02d}/{2:02d}'.format(first_day.year - 1911, first_day.month, first_day.day)

        for data in content['data5']:
            sign = '-' if data[9].find('green') > 0 else ''
            row = self._clean_row([
                date_str_record, # 日期
                data[2], # 成交股數
                data[4], # 成交金額
                data[5], # 開盤價
                data[6], # 最高價
                data[7], # 最低價
                data[8], # 收盤價
                sign + data[10], # 漲跌價差
                data[3], # 成交筆數
            ])
            self.tse_data[data[0].strip()] = row

    def _get_otc_data(self, date_str):
        ttime = str(int(time.time()*100))
        url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={}&_={}'.format(date_str, ttime)
        page = requests.get(url)

        if not page.ok:
            logging.error("Can not get OTC data at {}".format(date_str))
            return

        result = page.json()

        if result['reportDate'] != date_str:
            logging.error("Get error date OTC data at {}".format(date_str))
            return

        for table in [result['mmData'], result['aaData']]:
            for tr in table:
                row = self._clean_row([
                    date_str,
                    tr[8], # 成交股數
                    tr[9], # 成交金額
                    tr[4], # 開盤價
                    tr[5], # 最高價
                    tr[6], # 最低價
                    tr[2], # 收盤價
                    tr[3], # 漲跌價差
                    tr[10] # 成交筆數
                ])
                self._record(tr[0], row)

    def get_data(self, year, month, day):
        date_str = '{0}/{1:02d}/{2:02d}'.format(year - 1911, month, day)
        print 'Crawling {}'.format(date_str)
        if self._check_date(date_str) == False:
            print date_str + ' is already updated!'
            return False

        self._get_tse_data(date_str)    #上市股票
        #self._get_otc_data(date_str)   #上櫃股票 
        self._get_fund_data(date_str)   #三大法人
        
        #for key, value in self.tse_data.iteritems():
        for key in self.tse_data.keys():
            _record_row = {}
            if key in self.fund_data:
                _record_row = self.tse_data[key] + self.fund_data[key]
                pass
            else:
                _record_row = self.tse_data[key] + [0,0,0] 
            self._record(key, _record_row)
        print date_str + ' update successed!'
        return True

def main():
    # Set logging
    if not os.path.isdir('log'):
        os.makedirs('log')
    logging.basicConfig(filename='log/crawl-error.log',
        level=logging.ERROR,
        format='%(asctime)s\t[%(levelname)s]\t%(message)s',
        datefmt='%Y/%m/%d %H:%M:%S')

    # Get arguments
    parser = argparse.ArgumentParser(description='Crawl data at assigned day')
    parser.add_argument('day', type=int, nargs='*',
        help='assigned day (format: YYYY MM DD), default is today')
    parser.add_argument('-b', '--back', action='store_true',
        help='crawl back from assigned day until 2004/2/11')
    parser.add_argument('-c', '--check', action='store_true',
        help='crawl back 10 days for check data')

    args = parser.parse_args()

    # Day only accept 0 or 3 arguments
    if len(args.day) == 0:
        first_day = datetime.today()
    elif len(args.day) == 3:
        first_day = datetime(args.day[0], args.day[1], args.day[2])
    else:
        parser.error('Date should be assigned with (YYYY MM DD) or none')
        return

    #first_day = datetime(2017,03,02)
    crawler = Crawler()

    # If back flag is on, crawl till 2004/2/11, else crawl one day
    if args.back or args.check:
        # otc first day is 2007/04/20
        # tse first day is 2004/02/11

        last_day = datetime(2012, 1, 1) if args.back else first_day - timedelta(48)
        max_error = 5
        error_times = 0

        while error_times < max_error and first_day >= last_day:
            try:
                status = crawler.get_data(first_day.year, first_day.month, first_day.day)
                if status == False: 
                    break
                error_times = 0
            except:
                date_str = first_day.strftime('%Y/%m/%d')
                logging.error('Crawl get_data error {}'.format(date_str))
                error_times += 1
                continue
            finally:
                first_day -= timedelta(1)
    else:
        crawler.get_data(first_day.year, first_day.month, first_day.day)

if __name__ == '__main__':
    main()
