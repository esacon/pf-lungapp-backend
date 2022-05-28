import pymongo
from dotenv import load_dotenv
from os import environ as env

load_dotenv()  # take environment variables from .env.

# Enviroment variables.
USER = env.get('USER')
PASSWORD = env.get('PASSWORD')
DB = env.get('DB_NAME')

client = pymongo.MongoClient(f'mongodb+srv://{USER}:{PASSWORD}@breath-api.nlqhf.mongodb.net/{DB}?retryWrites=true&w=majority')
 
db = client.pf_db