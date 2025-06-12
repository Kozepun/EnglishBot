from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["mydatabase"]

users = db["users"]
groups = db["groups"]

users.delete_many({})
groups.delete_many({})
