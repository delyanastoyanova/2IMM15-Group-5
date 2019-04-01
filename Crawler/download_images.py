import csv
import urllib.request
import time

with open('data.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    image_number = 0
    for row in csv_reader:
        if image_number == 0:
            print(f'Column names are {", ".join(row)}')
            image_number += 1
        else:
            full_file_name = str(image_number) + '.jpg'
            urllib.request.urlretrieve(row[1],r"images\\"+full_file_name)
            print(f'\t{row[0]} image is downloaded.')
            image_number += 1
    print(f'Download completed.')
    print('Process time')
    print(time.process_time())
