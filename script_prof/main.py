import json
import pickle
import numpy as np
import random
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(dotenv_path="config")

class Massalia(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        self.words = pickle.load(open("models/words.pkl", "rb"))
        self.tags = pickle.load(open("models/tags.pkl", "rb"))
        self.model = load_model("models/chatbot_model.h5")
    
    def clean_up_sentence(self, sentence):
        lemmatizer = WordNetLemmatizer()
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
        return sentence_words
    
    def bag_of_words(self, sentence):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(self.words)
        for w in sentence_words :
            for i, word in enumerate(self.words):
                if word == w :
                    bag[i] = 1
        return np.array(bag)
    
    def predict_tag(self, sentence):
        bow = self.bag_of_words(sentence)
        res = self.model.predict(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent" : self.tags[r[0]], "probability" : str(r[1])})
        return return_list
    
    def get_response(self, intents_list, intents_json):
        tag = intents_list[0]["intent"]
        list_of_intents = intents_json["intents"]
        for i in list_of_intents:
            if i["tag"] == tag :
                result = random.choice(i["responses"])
                break
        return result

    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")
        
    async def on_message(self, message):
        if message.author.bot:
            return
        intents = json.loads(open('../data/intents.json').read())
        ints = self.predict_tag(message.content)
        res = self.get_response(ints, intents)
        if message.content.lower() == "ping":
            await message.channel.send("pong")
        else:
            await message.channel.send("{}".format(res))

bot = Massalia()
bot.run(os.getenv("TOKEN"))