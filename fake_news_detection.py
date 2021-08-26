# -*- coding: utf-8 -*-
"""Fake News Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uTwcysGHn1zG3CQClma0duJweMaYDnws
"""

from google.colab import drive
drive.mount('/content/drive/')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
import re 
from wordcloud import WordCloud

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, LSTM, Conv1D, MaxPooling1D
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score , confusion_matrix

fake = pd.read_csv(r"/content/drive/MyDrive/Fake_News_Detection/Dataset/Fake.csv")
fake.head()

fake.info()

fake.columns

fake['subject'].value_counts()

plt.figure(figsize=(10,6))
sns.countplot(x = 'subject' , data=fake)

fake['text']

fake['text'].tolist()

type(fake['text'].tolist())

text = ' '.join(fake['text'].tolist()) # list data convert into single string

type(text)

wordcloud = WordCloud(width=1920 , height=1080).generate(text)
fig = plt.figure(figsize = (10,10))
plt.imshow(wordcloud)
plt.axis('off')
plt.tight_layout(pad=0)
plt.show()

real = pd.read_csv(r"/content/drive/MyDrive/Fake_News_Detection/Dataset/True.csv")
real.head()

real.info()

real['subject'].value_counts()

plt.figure(figsize=(10,6))
sns.countplot(x = 'subject' , data=real)

text = ' '.join(real['text'].tolist()) # list data convert into single string

wordcloud = WordCloud(width=1920 , height=1080).generate(text)
fig = plt.figure(figsize = (10,10))
plt.imshow(wordcloud)
plt.axis('off')
plt.tight_layout(pad=0)
plt.show()

unknown_publishers = []

for index, row in enumerate(real.text.values):
    try:
        record = row.split('-' , maxsplit = 1)
        record[1]
        
        assert(len(record[0]) < 120)
    except:
        unknown_publishers.append(index)

len(unknown_publishers)

real.iloc[unknown_publishers]

real.iloc[8970]

real.drop(8970 , axis = 0)

real.iloc[unknown_publishers].text

publisher = []
tmp_text = []

for index, row in enumerate(real.text.values):
    if index in unknown_publishers:
        tmp_text.append(row)
        publisher.append('Unknown')
    else:
        record = row.split('-' , maxsplit = 1)
        publisher.append(record[0].strip())
        tmp_text.append(record[1].strip())

real['publisher'] = publisher
real['text'] = tmp_text

real.head()

empty_fake_index = [index for index,text in enumerate(fake.text.tolist()) if str(text).strip() == ""]

fake.iloc[empty_fake_index]

real['text'] = real['title'] + " " + real['text']
fake['text'] = fake['title'] + " " + fake['text']

real['text'] = real['text'].apply(lambda x: str(x).lower())
fake['text'] = fake['text'].apply(lambda x: str(x).lower())

real['class'] = 1
fake['class'] = 0

print(real.columns)
print(fake.columns)

real = real[['text' , 'class']]
fake = fake[['text' , 'class']]

data = real.append(fake, ignore_index = True)
data

data = data.sample(frac = 1 , random_state=42)
data

!pip install git+https://github.com/laxmimerit/preprocess_kgptalkie.git --upgrade --force-reinstall

import preprocess_kgptalkie as ps

data['text'] = data['text'].apply(lambda x: ps.remove_special_chars(x))

data.head() # word to numerical

import gensim

y = data['class'].values

X = [d.split() for d in data['text'].tolist()]
X

print(X[0])
print(X[1])
print(type(X))
print(type(X[0]))

DIM = 100 # word converted in sequence of 100 vector
w2v_model = gensim.models.Word2Vec(sentences = X , size=DIM , window=10 , min_count = 1) # vector_size = DIM for new

w2v_model.wv.vectors.shape

w2v_model.wv['love']

w2v_model.wv['india']

w2v_model.wv.most_similar('india') # word getting frequent with india article

tokenizer = Tokenizer()
tokenizer.fit_on_texts(X)

X = tokenizer.texts_to_sequences(X)

len(tokenizer.word_index)

[len(x) for x in X]

plt.hist([len(x) for x in X] , bins = 700)
plt.show()

nos = np.array([len(x) for x in X])
len(nos[nos>1000])

maxlen = 1000
X = pad_sequences(X , maxlen = maxlen)

len(X[1023])

vocab_size = len(tokenizer.word_index) + 1

vocab = tokenizer.word_index

def get_weight_matrix(model):
    weight_matrix = np.zeros((vocab_size , DIM))
    
    for word, i in vocab.items():
        weight_matrix[i] = model.wv[word]
        
    return weight_matrix

embedding_vectors = get_weight_matrix(w2v_model)

embedding_vectors.shape

model = Sequential()
model.add(Embedding(vocab_size , output_dim = DIM, weights = [embedding_vectors], input_length = maxlen, trainable = False ))
model.add(LSTM(units = 128))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer='adam' , loss = 'binary_crossentropy' , metrics = ['acc'])

model.summary()

X_train, X_test , y_train, y_test = train_test_split(X,y)

model.fit(X_train, y_train, validation_split = 0.3, epochs = 6)

y_pred = (model.predict(X_test) > 0.5).astype(int)

accuracy_score(y_test , y_pred)

print(classification_report(y_test, y_pred))

print(confusion_matrix(y_test, y_pred))

model.save('/content/drive/MyDrive/Fake_News_Detection/fake_news_detection.h5')

x = ['this is a new']
x = tokenizer.texts_to_sequences(x)
x = pad_sequences(x, maxlen = maxlen)
(model.predict(x) >= 0.5).astype(int)

