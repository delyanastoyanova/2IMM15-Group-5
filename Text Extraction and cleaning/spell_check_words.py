# in this program we are trying to clean the extracted text from the image
# first step will be to read the data from database
# then pass the noisy text to the cleaning function and return the clean text
# insert the clean text to the table in database


from nltk.tokenize import word_tokenize
import pymysql
import pandas
import time, datetime
import re, regex
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
import heapq
import enchant


# aws credentials
host = 'webirfacts.csdsyolim34i.us-east-2.rds.amazonaws.com'
port = 3306
username = 'group5'
password = 'aws12345'
dbname = 'facts_8'

# loading the dictionaries one time
spellcheck_US = enchant.Dict("en_US")
spellcheck_UK = enchant.Dict("en_UK")

# function to insert into table
def insert_into_table(clean_text, doc_id):

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    tuple_clean_text = (doc_id, clean_text, timestamp)

    conn_cursor.execute("INSERT INTO clean_text VALUES( % s, % s, % s)", tuple_clean_text)
    conn.commit()

# function to clean the data
def clean_data(noisy_text):
    lemmatizer = WordNetLemmatizer()

    # there are multiple rules that we want to check here
    # convert to lowercase
    # 1. convert currency symbols to words and remove the symbols
    # 2. include digits or decimals, any types of numbers
    # 3. remove stop words
    # 4. remove punctuation marks
    # 5. check if the word is an english word, but they are numbers then no need for this check


    # this dictionary is useful while lemmatizing the words
    pos_dict = { 'None':'n', '$':'n' ,'CC':'n', 'CD':'n', 'DT':'n', 'EX': 'n', 'FW': 'n', 'IN':'n', 'JJ': 'a', 'JJR':'a', 'JJS':'a',
                 'LS': 'n','MD': 'n','NN': 'n','NNS': 'n','NNP': 'n','NNPS': 'n','PDT': 'r','POS': 'n','PRP': 'n','PRP$': 'n','RB': 'r','RBR': 'r','RBS': 'r',
        'RP': 'n','TO': 'n','UH': 'n', 'VB': 'v', 'VBD': 'v','VBG': 'v', 'VBN': 'v','VBP': 'v','VBZ': 'v','WDT': 'n','WP': 'n','WP$': 'n','WRB': 'n', 'SYM': 'n'}

    # get the pos tags first
    noisy_data_pos_tag =  pos_tag(noisy_text.split())
    pos_tag_dict = {}
    # creating a dictionary of POS tags which will be used below
    for tags in noisy_data_pos_tag:
        clean_word = re.sub('[^\w\s]', '', tags[0])
        pos_tag_dict[clean_word] = tags[1]

    # changing the currency symbol to word here
    currency_dict = {'$': 'dollar', '€': 'euro', '₨': 'rupee', '¢' : 'cent', '£': 'pound', '¥': 'yen'}
    # regex to identify currency symbols
    currency_list = regex.findall(r'\p{Sc}', noisy_text)

    if (len(currency_list) != 0):
        for currency in currency_list:
        #     find at which position does the currency exist
            position = noisy_text.find(currency)
            if (position != -1):
                noisy_text = noisy_text[:position] + currency_dict[currency] + " "+ noisy_text[position:]


    # replace % by "percent" word
    percent_position = noisy_text.find('%')
    if percent_position != -1:
        noisy_text = noisy_text[:percent_position] + " percent " + noisy_text[percent_position:]

    clean_text = ""
    # removing the most frequent words
    for word in noisy_text.split():
        if word.lower() not in top_used_words:
            clean_text += word +" "

    # remove the stopwords here
    stopwords_list = stopwords.words('english')
    clean_text_stop = ""
    for word in word_tokenize(clean_text):
        if word.lower() not in stopwords_list and len(word) != 1 or word.isdigit() == True:
            clean_text_stop += word + " "

    clean_text_stop = clean_text_stop.lstrip().rstrip()

    english_text = ""
    for word in clean_text_stop.split():
        if word.lower()  in top_used_words:
            english_text += ""
        elif pos_tag_dict.get(word) == 'NNP':
            # check if the word is an english word
            if word.isupper():
                # it might be possible that NLTK identified the word as a proper noun bcoz of the upper case
                if spellcheck_US.check(word) or spellcheck_UK.check(word):
                    pos_tag_nnp = pos_tag([word])
                    conv_pos_tag = pos_dict.get(pos_tag_nnp[0][1])
                    lemmatized_word = lemmatizer.lemmatize(word.lower(), pos = conv_pos_tag)
                    english_text += lemmatized_word + " "
                else:
                    english_text += word + " "
            else:
                english_text += word + " "
#         here we have to perform spell check on the word
        elif spellcheck_US.check(word) or spellcheck_UK.check(word) or word.isdigit() or word.find('%') != -1 or re.search('(?=\S*[-])([a-zA-Z-]+)', word):
            # convert each word to its root form
            try:
                conv_pos_tag = str(pos_tag_dict.get(word))
                # lemmatizing the word
                lemmatized_word = lemmatizer.lemmatize(word.lower(), pos = pos_dict.get(conv_pos_tag))
                english_text += lemmatized_word+" "
            except:
                # if the word cannot be lemmatized then it should be dropped
                continue
        elif re.sub('[^\w\s]', '', word).isdigit() == True:
            english_text += word + " "
        else:
            continue
    #         end of loop


    # removing punctuation marks
    # doing this here  since we do not want to eliminate the hyphen-ated words
    english_text = re.sub('[^\w\s]', ' ', english_text)

    english_text = english_text.lstrip().rstrip().lower()
    print("Clean text: " + str(english_text))
    return english_text

# function to update the frequency of the words occuring in the corpus
def update_vocab(noisy_data):
    for word in noisy_data.lower().split(' '):
        if word in vocab_dictionary:
            vocab_dictionary[word] += 1
        else:
            vocab_dictionary[word] = 1
######################################################################################

# function call begins here
# setting up a connection to aws
conn = pymysql.connect(host, user=username,port=port, passwd=password, db=dbname)
conn_cursor = conn.cursor()


#get the extracted text from image from the database
get_noisy_data = 'select doc_id, noisy_data from noisy_text where noisy_data is not null or length(noisy_data) > 0'
noisy_text_df = pandas.read_sql(get_noisy_data, con = conn)
vocab_dictionary = {}

for data in noisy_text_df.itertuples():
    cleaned_text = ""
    doc_id = data[1]
    noisy_data = data[2]
    update_vocab(noisy_data)
# print(vocab_dictionary)
#
top_used_words = heapq.nlargest(150,  vocab_dictionary, vocab_dictionary.get)

# going through the data
for data in noisy_text_df.itertuples():
    print("--"+str(data[2]))
    cleaned_text = ""
    doc_id = data[1]
    if(pandas.isna(data[2]) == False and len(data[2].lstrip().rstrip()) != 0):
        # for each extracted text we pass it to the cleaning function
        cleaned_text = clean_data(data[2])

#     insert this into the table
    insert_into_table(cleaned_text, doc_id)


conn.close()
