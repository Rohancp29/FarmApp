from pymongo import MongoClient
from bcrypt import hashpw, gensalt

client = MongoClient("mongodb+srv://rohanpatil:Patil2909@farmapp.wuxmi.mongodb.net/?retryWrites=true&w=majority&appName=Farmapp")
db = client['FarmApp']
users_collection = db['users']


users = [
    {"name": "A", "role": "Field Executive", "password": "A"},
    {"name": "B", "role": "Field Executive", "password": "B"},
    {"name": "C", "role": "Field Manager", "password": "C"},
    {"name": "D", "role": "Field Manager", "password": "D"},
    {"name": "E", "role": "Senior Manager", "password": "E"}
]


for user in users:
    user['password'] = hashpw(user['password'].encode('utf-8'), gensalt()).decode('utf-8')

users_collection.delete_many({}) 
users_collection.insert_many(users)

print("Database initialized with encrypted passwords!")