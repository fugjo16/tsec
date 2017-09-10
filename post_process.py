import os
from datetime import datetime
import numpy as np
import pandas as pd

FOLDER = 'data'

IDX_5MA = 12
IDX_10MA = 13
IDX_20MA = 14
IDX_K9 = 15
IDX_D9 = 16

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
        
        rows[index,IDX_K9] = rows[index+1, IDX_K9]*2/3 + rsv*1/3                         # val_K
        rows[index,IDX_D9] = rows[index+1, IDX_D9]*2/3 + rows[index,IDX_K9]*1/3          # val_D
    return rows

def get_avg_line(rows):

    return rows
    
def get_bbands(rows):
    
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
    for file_name in file_names:
        if not file_name.endswith('.csv'):
            continue
        
        stock_data, rows = get_csv(file_name)
        length = min(len(rows), 90)
        rows = rows[:length]
        
#        rows = get_avg_line(rows)
        rows = get_kd_value(rows)
#        rows = get_bbands(rows)

        # Write to CSV
        df = pd.DataFrame(data=rows[0:,0:], columns=stock_data.columns)  # values, columns
        df.to_csv("test.csv", index=False)

if __name__ == '__main__':
    main()