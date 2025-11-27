import pymongo
import os
import dotenv

dotenv.load_dotenv()

# MongoDB connection setup
MONGO_STRING = os.getenv("MONGO_STRING")
client = pymongo.MongoClient(MONGO_STRING)
database = client["Processed-Orders"]
collection = database["processed_orders"]


def main(reffNumber):
    existing_document = collection.find_one({"_id": reffNumber})
    if existing_document:
        print("Found document for {}".format(reffNumber))
    else:
        print("Document not found for {}".format(reffNumber))



if __name__ == "__main__":
    reffNumber = "AI021438-001"
    main(reffNumber)
        

