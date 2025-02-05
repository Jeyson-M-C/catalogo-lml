from motor.motor_asyncio import AsyncIOMotorClient 
MONGO_URI = 'mongodb+srv://lmenslmental:K16agEJDVz98j9qY@catalogo-lml.qpeit.mongodb.net/'
MONGO_DB = 'catalogo-lml'

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
