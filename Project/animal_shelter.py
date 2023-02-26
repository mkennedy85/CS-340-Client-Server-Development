from pymongo import MongoClient
from bson.objectid import ObjectId
from os import getenv
import json

class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, username='', password=''):
        # Initializing the MongoClient. This helps to 
        # access the MongoDB databases and collections. 
        # self.client = MongoClient('mongodb://%s:%s@localhost:49312' % (username, password))
        self.client = MongoClient('mongodb://%s:%s@localhost:27017' % (username, password))
        self.database = self.client['AAC']

    def create(self, data):
        """
        create(data)

        Create new documents by providing dictionary to insert.
        """
        if data is not None:
            if type(data) is dict:
                try:
                    self.database.animals.insert(data)  # data should be dictionary
                    return True
                except:
                    return False
            else:
                raise Exception("Unable to create document as input is not of type dictionary")
        else:
            raise Exception("Nothing to save, because data parameter is empty")

    def read(self, query=None):
        """
        read(query || None)

        Read from database providing an optional query  and return cursor object at first result.
        """
        if (query is None) or (type(query) is dict):
            return self.database.animals.find(query, {'_id': False})
        else:
            raise Exception("Unable to query database as read may except no arguments or dictionary only")

    def read_all(self):
        """
        read_all()

        Read from database returning all results.
        """
        return self.database.animals.find({}, {'_id': False})

    def update(self, query=None, data=None):
        """
        update(query, data)

        Update documents from query with data. Data is required and will result in an
        Exception if no data is provided or data is not of type dictionary.
        """
        if ((query is not None) and (type(query) is dict)):
            if (type(data) is dict):
                try:
                    result = self.database.animals.update_many(query, {"$set": data})
                    return json.dumps(result.raw_result)
                except:
                    raise
            else:
                raise Exception("Data must be provided as dictionary to update documents")
        else:
            raise Exception("Query must be provided and of type dictionary.")

    def delete(self, query=None):
        """
        delete(query)

        Delete records returned from query. Query must be provided and of type dictionary.
        """
        if ((query is not None) and (type(query) is dict)):
            try:
                result = self.database.animals.delete_many(query)
                return json.dumps(result.raw_result)
            except:
                raise
        else:
            raise Exception("Query must be provided and of type dictionary.")
