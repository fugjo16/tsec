import os
from datetime import datetime

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
    datas = row.split(',')
    if len(datas) <= 12:
        datas[len(datas) - 1] = datas[len(datas) - 1].strip('\n')
        datas.append('50')
        datas.append('50\n')
    str_row = ''
    for key in datas:
        str_row += key + ','

    return str_row[:len(str_row)-1]

def get_kd_value(rows):
    if len(rows) < 10:
        return 

    last_day = len(rows)-8
    rows[last_day] = check_kd_init(rows[last_day])

    for index in range(last_day-1, -1, -1):
        max_9 = 0.0
        min_9 = 99999999.0
        price = float(rows[index].split(',')[6])
        for i in range(9):
            row = rows[index + i]
            value = float(row.split(',')[6])
            if value > max_9: max_9 = value
            if value < min_9: min_9 = value

        rsv = (price - min_9) / (max_9 - min_9) * 100 if (max_9 != min_9) else 0
        
        if len(rows[index].split(',')) <= 12:
            val_k = float(rows[index+1].split(',')[12])*2/3 + rsv*1/3
            val_d = float(rows[index+1].split(',')[13])*2/3 + val_k*1/3
            rows[index] = rows[index][:len(rows[index])-1] + ',' + '%.1f'%(val_k) + ',' + '%.1f'%(val_d) + '\n'

def main():
    file_names = os.listdir(FOLDER)
    for file_name in file_names:
        if not file_name.endswith('.csv'):
            continue

        dict_rows = {}

        # Load and remove duplicates (use newer)
        with open('{}/{}'.format(FOLDER, file_name), 'rb') as file:
            lines = file.readlines()
            for i in range(1, len(lines)):  # Remove row header
                line = lines[i]
                dict_rows[line.split(',', 1)[0]] = line

        # Sort by date
        rows = [row for date, row in sorted(
            dict_rows.items(), key=lambda x: string_to_time(x[0]), reverse=True)]

        length = min(len(rows), 90)
        rows = rows[:length]
        get_kd_value(rows)
        with open('{}/{}'.format(FOLDER, file_name), 'wb') as file:
            row_header = ['Date,Volume,Value,Open,High,Low,Close,Charge,Number,Foreign,Invest,Dealer,K_9,D_9\n']
            rows = row_header + rows
            file.writelines(rows)

if __name__ == '__main__':
    main()