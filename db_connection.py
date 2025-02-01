import pymongo

from pymongo import MongoClient

# Replace with your actual MongoDB connection details
client = MongoClient('mongodb://localhost:27017')
db = client['Products']