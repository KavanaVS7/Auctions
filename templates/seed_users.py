from pymongo import MongoClient

# MongoDB URI (escaped password with @ and #)
mongo_uri = "mongodb+srv://varsha:%40Hello12345%23@cluster0.s14ztnw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)

# Use the correct DB and collection
db = client["auction_platform"]
users_collection = db["USERS"]
#categories_collection=db["CATEGORIES"]

# Clear existing users (optional, for testing)
users_collection.delete_many({})
#categories_collection.delete.many({})
# Generate 60 users
users = []
for i in range(1, 61):
    user = {
        "name": f"User{i}",
        "email": f"user{i}@example.com",
        "password": "pass123",
        "role": "seller" if i % 2 == 1 else "buyer"
    }
    users.append(user)
#categories = []
#for i in range(1,61):
 #   categories = {

  #  }

# Insert into MongoDB
users_collection.insert_many(users)

print("Inserted 60 users.")

