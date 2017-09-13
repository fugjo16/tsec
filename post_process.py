import os
from datetime import datetime
import numpy as np
import pandas as pd

FOLDER = 'data'

IDX_CLOSE = 6
IDX_5MA = 12
IDX_10MA = 13
IDX_20MA = 14
IDX_K9 = 15
IDX_D9 = 16
IDX_UPB = 17
IDX_LWB = 18
IDX_PB = 19
IDX_BW = 20

def string_to_time(string):
    year, month, day = string.split('/')
    return datetime(int(year) + 1911, int(month), int(day))

def is_same(row1, row2):
    if not len(row1) == len(row2):
        return False

    for index in range(len(row1)):
        if row1[index] != row2[index]:
            return False
    else:
        return True
    
def check_kd_init(stock_data):
    if len(stock_data.columns) < 13:
        stock_data['5MA'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)
        stock_data['10MA'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)
        stock_data['20MA'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)
    if len(stock_data.columns) < 16:
        stock_data['K_9'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)
        stock_data['D_9'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)
    if len(stock_data.columns) < 18:
        stock_data['Upper_Band'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)
        stock_data['Lower_Band'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)
        stock_data['PB'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)        # Persent B, PB
        stock_data['BW'] = pd.Series(np.full(len(stock_data), -1.0), index=stock_data.index)        # Bandwidth, BW
        
    return stock_data

def get_kd_value(rows):
    if len(rows) < 10:
        return rows

    last_day = len(rows)-8
    if rows[last_day, IDX_K9] < 0 or rows[last_day, IDX_D9] < 0:
        rows[last_day, IDX_K9] = rows[last_day, IDX_D9] = 50    # initialization
    
    for index in range(last_day-1, -1, -1):
        if rows[index,IDX_K9] > 0 and rows[index,IDX_D9] > 0:
            continue
        
        max_9 = max(rows[index:index+9, 4])     # Highest Price
        min_9 = min(rows[index:index+9, 5])     # Lowest Price
    
        price = rows[index, 6]
        rsv = (price - min_9) / (max_9 - min_9) * 100 if (max_9 != min_9) else 0
        
        rows[index,IDX_K9] = round(rows[index+1, IDX_K9]*2/3 + rsv*1/3, 2)                         # val_K
        rows[index,IDX_D9] = round(rows[index+1, IDX_D9]*2/3 + rows[index,IDX_K9]*1/3, 2)          # val_D
    return rows

def get_avg_line(rows):
    if len(rows) > 20:
        last_day = len(rows)-20
        for index in range(last_day-1, -1, -1):
            if rows[index, IDX_5MA] < 0:
                rows[index, IDX_5MA] = round(sum(rows[index:index+5, IDX_CLOSE]) / 5, 2)
            if rows[index, IDX_10MA] < 0:
                rows[index, IDX_10MA] = round(sum(rows[index:index+10, IDX_CLOSE]) / 10, 2)
            if rows[index, IDX_20MA] < 0:
                rows[index, IDX_20MA] = round(sum(rows[index:index+20, IDX_CLOSE]) / 20, 2)
#                rows[index, IDX_20MA] = sum(sum(rows[index:index+20, 4:6])) / 40    # 20MA with Min-Max
    return rows
    
def get_bbands(rows):
    if len(rows) > 20:
        last_day = len(rows)-20
        for index in range(last_day-1, -1, -1):
            if rows[index, IDX_20MA] <= 0:
                continue
            sdt = np.std(rows[index:index+20, 6])
            rows[index, IDX_UPB] = round(rows[index, IDX_20MA] + 2.1*sdt, 2)
            rows[index, IDX_LWB] = round(rows[index, IDX_20MA] - 2.1*sdt, 2)
            rows[index, IDX_PB] = round((rows[index, IDX_CLOSE] - rows[index, IDX_LWB]) / (4.2*sdt), 4)
            rows[index, IDX_BW] = round(4.2*sdt / rows[index, IDX_20MA], 4)
    return rows

def get_csv(file_name):
    stock_data = pd.read_csv(FOLDER+'/'+file_name)
    stock_data = check_kd_init(stock_data)
    
    rows = stock_data.iloc[:,:].values
    rows = rows[rows[:, 0].argsort()][::-1]
    return stock_data, rows
#    dict_rows = {}
#    # Load and remove duplicates (use newer)
#    with open('{}/{}'.format(FOLDER, file_name), 'rb') as file:
#        lines = file.readlines()
#        for i in range(1, len(lines)):  # Remove row header
#            line = lines[i]
#            dict_rows[line.split(',', 1)[0]] = line
#
#    # Sort by date
#    rows = [row for date, row in sorted(
#        dict_rows.items(), key=lambda x: string_to_time(x[0]), reverse=True)]
#    return rows

def main():
    file_names = os.listdir(FOLDER)
    process = counter = 0
    for file_name in file_names:
        if not file_name.endswith('.csv'):
            continue
        
        # Get last 3 months data
        stock_data, rows = get_csv(file_name)
        length = min(len(rows), 90)
        rows = rows[:length]
        
        # Get technical value
        rows = get_avg_line(rows)
        rows = get_kd_value(rows)
        rows = get_bbands(rows)

        # Write to CSV
        df = pd.DataFrame(data=rows[0:,0:], columns=stock_data.columns)  # values, columns
        df.to_csv(FOLDER+'/'+file_name, index=False)
        
        # Print progress
        counter += 1
        if counter*100/len(file_names) >= process+20:
            process += 20
            print(str(process) + '%')

if __name__ == '__main__':
    main()