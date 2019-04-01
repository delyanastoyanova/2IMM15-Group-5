import pandas, pymysql
from gensim.models import KeyedVectors
import numpy as np

def create_feature_vectors(corpus, doc_id_list):
#     here we use the pre trained model for creating feature vectors
    model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
    for doc in corpus:
        # print(doc)
        word_vector = []
        # word_vector = [model[x] for x in doc.split(' ')]
        for x in doc.split(' '):
            try:
                word_vector.append(model[x])
                # print("---"+str(len(model[x])))
            except KeyError:
                # print("word "+str(x)+" not in vocab")
                # word_not_in_vocab.append(x)
                word_vector.append(np.array([0] * 300))
    # create a list of zeroes

    # print(word_vector)
    #     this word vector is for each document, we need to figure out how to use this word vector further
    # print(word_not_in_vocab)

host = 'webirfacts.csdsyolim34i.us-east-2.rds.amazonaws.com'
port = 3306
username = 'group5'
password = 'aws12345'
dbname = 'facts_8'

# setting up a connection to aws
conn = pymysql.connect(host, user=username,port=port, passwd=password, db=dbname)
conn_cursor = conn.cursor()

# we need to create a corpus first
#get the cleaned extracted text from image from the database
get_clean_data = 'select doc_id, clean_data from clean_text where clean_data is not null or length(clean_data) > 0'
clean_text_df = pandas.read_sql(get_clean_data, con = conn)

corpus = []
doc_id_list = []
for data in clean_text_df.itertuples():
    corpus.append(data[2])
    doc_id_list.append(data[1])
# pass this corpus to the feature vector generator
# create_feature_vectors(corpus)
create_feature_vectors(corpus, doc_id_list)
