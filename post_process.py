import os
from datetime import datetime
import numpy as np
import pandas as pd

FOLDER = 'data'


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
    
def check_kd_init(row):
    if (np.isnan(row[12])):
        row[12] = row[13] = 50
    return row

def get_kd_value(rows):
    if len(rows) < 10:
        return 

    last_day = len(rows)-8
    rows[last_day] = check_kd_init(rows[last_day])

    for index in range(last_day-1, -1, -1):
        max_9 = 0.0
        min_9 = 99999999.0
        price = float(rows[index, 6])
        for i in range(9):
            value = float(rows[index+i, 6])
            if value > max_9: max_9 = value
            if value < min_9: min_9 = value
    
        rsv = (price - min_9) / (max_9 - min_9) * 100 if (max_9 != min_9) else 0
        
        if (np.isnan(rows[index, 12])):
            val_k = float(rows[index+1,12])*2/3 + rsv*1/3
            val_d = float(rows[index+1,13])*2/3 + val_k*1/3
            rows[index,12] = val_k
            rows[index,13] = val_d

def get_bbands(rows):
    print((rows))

def get_csv(file_name):
    stock_data = pd.read_csv(FOLDER+'/'+file_name)
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
        get_kd_value(rows)
        #get_bbands(rows)

        # Write to CSV
        df = pd.DataFrame(data=rows[0:,0:], columns=stock_data.columns)  # values, columns
        df.to_csv("test.csv", index=False)

if __name__ == '__main__':
    main()