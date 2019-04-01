# in this program we are trying to extract the text from an image
# first step will be to read the image
# then convert it to black and white format, keeping black text and white background
# lets see how it goes

# Convert color to grayscale and set a binary threshold
# so everything is either black or white.

import os, cv2
import pytesseract, numpy as np
import datetime, time
import pymysql

host = 'webirfacts.csdsyolim34i.us-east-2.rds.amazonaws.com'
port = 3306
username = 'group5'
password = 'aws12345'
dbname = 'facts_8'


# setting up a connection to aws
conn = pymysql.connect(host, user=username,port=port, passwd=password, db=dbname)
conn_cursor = conn.cursor()

# function to insert data into table
def insert_into_table(noisy_text, filename):

    doc_id = filename.split('.')[0]
    print(str(doc_id)+"|"+str(noisy_text))
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    tuple_noisy_text = (doc_id, noisy_text, timestamp)

    conn_cursor.execute("INSERT INTO noisy_text VALUES( % s, % s, % s)", tuple_noisy_text)
    conn.commit()

def access_image(filename):
    image = cv2.imread(filename)
    return image

def convert_to_grayscale(image_read):
    # convert the image to greayscale
    gray_scale_image = cv2.cvtColor(image_read, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    gray_scale_image = cv2.dilate(gray_scale_image, kernel, iterations=1)

    # convert the grey scale image to monochrome
    otsu_img = cv2.threshold(gray_scale_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    cv2.imwrite('/home/deb/TUE/Q3/Web_IR/otsu_image.jpg', otsu_img)

    # extract the text from monochrome image using OCR
    text = pytesseract.image_to_string(otsu_img, lang="eng", config='--psm 13')
    filtered = ""
    # this is done to remove the excess whitelines from the extracted text
    for lines in text.splitlines():
        filtered += lines +" "
    #     removing any extra white spaces if any
    return filtered.lstrip().rstrip()


# path where the images are stored
path = '/home/deb/TUE/Q3/Web_IR/images_final'
os.chdir(path)

filenames_list = os.listdir(path)
# for each file call the above functions
for file in filenames_list:
    image_read = access_image(file)
    noisy_text = convert_to_grayscale(image_read)
    insert_into_table(noisy_text, file)

cv2.waitKey(0)
conn.close()
