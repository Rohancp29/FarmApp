from pymongo import MongoClient

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

users_collection.delete_many({}) 
users_collection.insert_many(users)
print("Database initialized!")
