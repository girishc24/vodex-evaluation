from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

# MongoDB cluster connection string from .env file
MONGO_DETAILS = config("MONGO_DETAILS")

# Create a MongoDB client
client = AsyncIOMotorClient(MONGO_DETAILS)

# Define the database and collections
database = client['vodex']
items_collection = database.get_collection('items')
clockin_collection = database.get_collection('clockin')
