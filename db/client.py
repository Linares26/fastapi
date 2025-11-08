from pymongo import MongoClient
from pymongo.server_api import ServerApi

#db_client = MongoClient().local


db_client = MongoClient("mongodb+srv://claridaily_db_user:Uoc72dNDFH9BQBFO@cluster0.whakrzb.mongodb.net/?appName=Cluster0", server_api=ServerApi('1')).claridaily_db_user

try:
    db_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

