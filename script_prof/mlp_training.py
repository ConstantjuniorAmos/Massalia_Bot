import random
import json
import pickle
import numpy as np

import nltk
nltk.download()
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD

lemmatizer = WordNetLemmatizer()

intents = json.loads(open('data/intents.json').read())

words = []
tags = []
documents = []
ignore_letters = ["?", "!", ".", ","]

for intent in intents['intents'] :
    for pattern in intent["patterns"]:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in tags :
            tags.append(intent['tag'])

words = [lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]

words = sorted(set(words))
tags = sorted(set(tags))

pickle.dump(words, open("models/words.pkl", "wb"))
pickle.dump(tags, open("models/tags.pkl", "wb"))

training = []
output_empty = [0] * len(tags)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_pattenrs = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)
    
    output_row = list(output_empty)
    output_row[tags.index(document[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)

training = np.array(training, dtype=object)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation = "relu"))
model.add(Dropout(0.5))
model.add(Dense(64, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation="softmax"))
print(model.summary())

sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

h = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save("models/chatbot_model.h5", h)
print("Done training.")